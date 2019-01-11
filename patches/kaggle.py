import os
from google.auth import credentials
from google.cloud import bigquery
from google.cloud.bigquery._http import Connection


class KaggleKernelCredentials(credentials.Credentials):
    """Custom Credentials used to authenticate using the Kernel's connected OAuth account.

    Example usage:
    client = bigquery.Client(project='ANOTHER_PROJECT',
                                credentials=KaggleKernelCredentials())
    """

    def refresh(self, request):
        print("Calling Kaggle.UserSecrets to refresh token.")
        # Set self.token and self.expiry here.
        raise NotImplementedError(
            "Private BigQuery integration is not yet implemented.")


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

    def __init__(self, project=None):
        if project:
            raise Exception("In order to query a private BigQuery project, please connect a GCP account. "
                            "Otherwise do not specify a project to use Kaggle's public dataset BigQuery integration.")
        data_proxy_project = os.getenv("KAGGLE_DATA_PROXY_PROJECT")
        anon_credentials = credentials.AnonymousCredentials()
        anon_credentials.refresh = lambda *args: None
        super().__init__(
            project=data_proxy_project, credentials=anon_credentials
        )
        self._connection = _DataProxyConnection(self)
