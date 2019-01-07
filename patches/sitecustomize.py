from google.auth import credentials
from google.cloud import bigquery
from google.cloud.bigquery._http import Connection
import os


class KaggleKernelCredentials(credentials.Credentials):
    """Custom Credentials used to authenticate using the Kernel's connected OAuth account."""

    def refresh(self, request):
        print("Calling Kaggle.UserSecrets to refresh token.")
        # Set self.token and self.expiry here.
        raise NotImplementedError("Private BigQuery integration is not yet implemented.")

kaggle_proxy_token = os.getenv("KAGGLE_DATA_PROXY_TOKEN")
CONNECTION_BASE_URL = Connection.API_BASE_URL


def monkeypatch_bq(bq_client, *args, **kwargs):
    data_proxy_project = os.getenv("KAGGLE_DATA_PROXY_PROJECT")
    bq_user_jwt = os.getenv("KAGGLE_BQ_USER_JWT")
    specified_project = kwargs.get('project')
    # Use Data Proxy if user has specified to use the Kaggle project, or if
    # there are no connected GCP accounts (to maintain backwards compatibility).
    if bq_user_jwt is None and specified_project and specified_project.lower() != 'kaggle':
        raise Exception("In order to query a private BigQuery project, please connect a GCP account. "
                        "Otherwise specify 'kaggle' as the project to use Kaggle's public dataset BigQuery integration.")
    use_data_proxy = (specified_project and specified_project.lower() == 'kaggle') or bq_user_jwt is None
    if use_data_proxy:
        if data_proxy_project is None or kaggle_proxy_token is None:
            # We don't have the data proxy info so leave the bq client unmodified.
            return bq_client(*args, **kwargs)
        print("Using Kaggle's public dataset BigQuery integration.")
        Connection.API_BASE_URL = os.getenv("KAGGLE_DATA_PROXY_URL")
        Connection._EXTRA_HEADERS["X-KAGGLE-PROXY-DATA"] = kaggle_proxy_token
        anon_credentials = credentials.AnonymousCredentials()
        anon_credentials.refresh = lambda *args: None
        kwargs['project'] = data_proxy_project
        return bq_client(
            *args,
            credentials=anon_credentials,
            **kwargs)
    else:
        Connection.API_BASE_URL = CONNECTION_BASE_URL
        Connection._EXTRA_HEADERS.pop('X-KAGGLE-PROXY-DATA', None)
        if kwargs.get('credentials') is not None:
            # The user wants to use their own credentials scheme, don't try to interfere.
            return bq_client(*args, **kwargs)
        print("Using enabled BigQuery integration.")
        kwargs['credentials'] = KaggleKernelCredentials()
        return bq_client(
            *args,
            **kwargs)

# Monkey patches BigQuery client creation to use proxy or user.
bq_client = bigquery.Client
bigquery.Client = lambda *args, **kwargs:  monkeypatch_bq(bq_client, *args, **kwargs)

