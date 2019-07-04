import os
from google.auth import credentials
from google.auth.exceptions import RefreshError
from google.cloud import bigquery
from google.cloud.exceptions import Forbidden
from google.cloud.bigquery._http import Connection
from kaggle_secrets import GcpTarget, UserSecretsClient

from log import Log


def get_integrations():
    kernel_integrations_var = os.getenv("KAGGLE_KERNEL_INTEGRATIONS")
    kernel_integrations = KernelIntegrations()
    if kernel_integrations_var is None:
        return kernel_integrations
    for integration in kernel_integrations_var.split(':'):
        try:
            target = GcpTarget[integration.upper()]
            kernel_integrations.add_integration(target)
        except KeyError as e:
            Log.error(f"Unknown integration target: {e}")
    return kernel_integrations


class KernelIntegrations():
    def __init__(self):
        self.integrations = {}

    def add_integration(self, target):
        self.integrations[target] = True

    def has_integration(self, target):
        return target in self.integrations

    def has_bigquery(self):
        return GcpTarget.BIGQUERY in self.integrations

    def has_gcs(self):
        return GcpTarget.GCS in self.integrations


class KaggleKernelCredentials(credentials.Credentials):
    """Custom Credentials used to authenticate using the Kernel's connected OAuth account.
    Example usage:
    client = bigquery.Client(project='ANOTHER_PROJECT',
                                credentials=KaggleKernelCredentials())
    """
    def __init__(self, target=GcpTarget.BIGQUERY):
        super().__init__()
        self.target = target

    def refresh(self, request):
        try:
            client = UserSecretsClient()
            if self.target == GcpTarget.BIGQUERY:
                self.token, self.expiry = client.get_bigquery_access_token()
            elif self.target == GcpTarget.GCS:
                self.token, self.expiry = client._get_gcs_access_token()
        except ConnectionError as e:
            Log.error(f"Connection error trying to refresh access token: {e}")
            print("There was a connection error trying to fetch the access token. "
                  f"Please ensure internet is on in order to use the {self.target.service} Integration.")
            raise RefreshError('Unable to refresh access token due to connection error.') from e
        except Exception as e:
            Log.error(f"Error trying to refresh access token: {e}")
            if (not get_integrations().has_integration(self.target)):
                Log.error(f"No {self.target.service} integration found.")
                print(
                   f"Please ensure you have selected a {self.target.service} account in the Kernels Settings sidebar.")
            raise RefreshError('Unable to refresh access token.') from e


class _DataProxyConnection(Connection):
    """Custom Connection class used to proxy the BigQuery client to Kaggle's data proxy."""

    API_BASE_URL = os.getenv("KAGGLE_DATA_PROXY_URL")

    def __init__(self, client):
        super().__init__(client)
        self.extra_headers["X-KAGGLE-PROXY-DATA"] = os.getenv(
            "KAGGLE_DATA_PROXY_TOKEN")

    def api_request(self, *args, **kwargs):
        """Wrap Connection.api_request in order to handle errors gracefully.
        """
        try:
            return super().api_request(*args, **kwargs)
        except Forbidden as e:
            msg = ("Permission denied using Kaggle's public BigQuery integration. "
                   "Did you mean to select a BigQuery account in the Kernels Settings sidebar?")
            print(msg)
            Log.info(msg)
            raise e


class PublicBigqueryClient(bigquery.client.Client):
    """A modified BigQuery client that routes requests using Kaggle's Data Proxy to provide free access to Public Datasets.
    Example usage:
    from kaggle import PublicBigqueryClient
    client = PublicBigqueryClient()
    """

    def __init__(self, *args, **kwargs):
        data_proxy_project = os.getenv("KAGGLE_DATA_PROXY_PROJECT")
        anon_credentials = credentials.AnonymousCredentials()
        anon_credentials.refresh = lambda *args: None
        super().__init__(
            project=data_proxy_project, credentials=anon_credentials, *args, **kwargs
        )
        # TODO: Remove this once https://github.com/googleapis/google-cloud-python/issues/7122 is implemented.
        self._connection = _DataProxyConnection(self)
