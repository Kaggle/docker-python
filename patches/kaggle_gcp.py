import os
from google.auth import credentials
from google.auth.exceptions import RefreshError 
from google.cloud import bigquery
from google.cloud.bigquery._http import Connection
from kaggle_secrets import UserSecretsClient


class KaggleKernelCredentials(credentials.Credentials):
    """Custom Credentials used to authenticate using the Kernel's connected OAuth account.
    Example usage:
    client = bigquery.Client(project='ANOTHER_PROJECT',
                                credentials=KaggleKernelCredentials())
    """

    def refresh(self, request):
        print("Calling Kaggle.UserSecrets to refresh token.")
        try:
            client = UserSecretsClient()
            fresh_token = client.get_bigquery_access_token()
        except Exception as e:
            raise RefreshError('Unable to refresh access token.') from e


class _DataProxyConnection(Connection):
    """Custom Connection class used to proxy the BigQuery client to Kaggle's data proxy."""

    API_BASE_URL = os.getenv("KAGGLE_DATA_PROXY_URL")

    def __init__(self, client):
        super().__init__(client)
        self._EXTRA_HEADERS["X-KAGGLE-PROXY-DATA"] = os.getenv(
            "KAGGLE_DATA_PROXY_TOKEN")


class PublicBigqueryClient(bigquery.client.Client):
    """A modified BigQuery client that routes requests using Kaggle's Data Proxy to provide free access to Public Datasets.
    Example usage:
    from kaggle import PublicBigqueryClient
    client = PublicBigqueryClient()
    """

    def __init__(self):
        data_proxy_project = os.getenv("KAGGLE_DATA_PROXY_PROJECT")
        anon_credentials = credentials.AnonymousCredentials()
        anon_credentials.refresh = lambda *args: None
        super().__init__(
            project=data_proxy_project, credentials=anon_credentials
        )
        # TODO: Remove this once https://github.com/googleapis/google-cloud-python/issues/7122 is implemented.
        self._connection = _DataProxyConnection(self)
