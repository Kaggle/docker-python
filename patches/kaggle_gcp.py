import os
from google.auth import credentials
from google.auth.exceptions import RefreshError
from google.cloud import bigquery
from google.cloud.exceptions import Forbidden
from google.cloud.bigquery._http import Connection
from kaggle_secrets import UserSecretsClient


def get_integrations():
    kernel_integrations_var = os.getenv("KAGGLE_KERNEL_INTEGRATIONS")
    kernel_integrations = KernelIntegrations()
    if kernel_integrations_var is None:
        return kernel_integrations
    for integration in kernel_integrations_var.split(':'):
        kernel_integrations.add_integration(integration.lower())
    return kernel_integrations


class KernelIntegrations():
    def __init__(self):
        self.integrations = {}

    def add_integration(self, integration_name):
        self.integrations[integration_name] = True

    def has_bigquery(self):
        return 'bigquery' in self.integrations.keys()


class KaggleKernelCredentials(credentials.Credentials):
    """Custom Credentials used to authenticate using the Kernel's connected OAuth account.
    Example usage:
    client = bigquery.Client(project='ANOTHER_PROJECT',
                                credentials=KaggleKernelCredentials())
    """

    def refresh(self, request):
        try:
            client = UserSecretsClient()
            self.token, self.expiry = client.get_bigquery_access_token()
        except ConnectionError as e:
            print("There was a connection error trying to fetch the access token. "
                  "Please ensure internet is on in order to use the BigQuery Integration.")
            raise RefreshError('Unable to refresh access token due to connection error.') from e
        except Exception as e:
            if (not get_integrations().has_bigquery()):
                print(
                    'Please ensure you have selected a BigQuery account in the Kernels Settings sidebar.')
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
            super().api_request(*args, **kwargs)
        except Forbidden as e:
            print("Permission denied using Kaggle's public BigQuery integration. "
                  "Did you mean to select a BigQuery account in the Kernels Settings sidebar?")
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
