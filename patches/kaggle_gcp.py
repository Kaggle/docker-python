import os
import inspect
from google.auth import credentials
from google.auth.exceptions import RefreshError
from google.api_core.gapic_v1.client_info import ClientInfo
from google.cloud import bigquery
from google.cloud.exceptions import Forbidden
from google.cloud.bigquery._http import Connection
from kaggle_secrets import GcpTarget, UserSecretsClient

from log import Log

KAGGLE_GCP_CLIENT_USER_AGENT="kaggle-gcp-client/1.0"

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

    def has_automl(self):
        return GcpTarget.AUTOML in self.integrations


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
            elif self.target == GcpTarget.AUTOML:
                self.token, self.expiry = client._get_automl_access_token()
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
                   f"Please ensure you have selected a {self.target.service} account in the Notebook Add-ons menu.")
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
                   "Did you mean to select a BigQuery account in the Notebook Add-ons menu?")
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

def has_been_monkeypatched(method):
    return "kaggle_gcp" in inspect.getsourcefile(method)

def init_bigquery():
    from google.auth import environment_vars
    from google.cloud import bigquery

    is_proxy_token_set = "KAGGLE_DATA_PROXY_TOKEN" in os.environ
    is_user_secrets_token_set = "KAGGLE_USER_SECRETS_TOKEN" in os.environ
    if not (is_proxy_token_set or is_user_secrets_token_set):
        return bigquery

    # If this Notebook has bigquery integration on startup, preload the Kaggle Credentials
    # object for magics to work.
    if get_integrations().has_bigquery():
        from google.cloud.bigquery import magics
        magics.context.credentials = KaggleKernelCredentials()

    def monkeypatch_bq(bq_client, *args, **kwargs):
        from kaggle_gcp import get_integrations, PublicBigqueryClient, KaggleKernelCredentials
        specified_credentials = kwargs.get('credentials')
        has_bigquery = get_integrations().has_bigquery()
        # Prioritize passed in project id, but if it is missing look for env var.
        arg_project = kwargs.get('project')
        explicit_project_id = arg_project or os.environ.get(environment_vars.PROJECT)
        # This is a hack to get around the bug in google-cloud library.
        # Remove these two lines once this is resolved:
        # https://github.com/googleapis/google-cloud-python/issues/8108
        if explicit_project_id:
            Log.info(f"Explicit project set to {explicit_project_id}")
            kwargs['project'] = explicit_project_id
        if explicit_project_id is None and specified_credentials is None and not has_bigquery:
            msg = "Using Kaggle's public dataset BigQuery integration."
            Log.info(msg)
            print(msg)
            return PublicBigqueryClient(*args, **kwargs)
        else:
            if specified_credentials is None:
                Log.info("No credentials specified, using KaggleKernelCredentials.")
                kwargs['credentials'] = KaggleKernelCredentials()
                if (not has_bigquery):
                    Log.info("No bigquery integration found, creating client anyways.")
                    print('Please ensure you have selected a BigQuery '
                        'account in the Notebook Add-ons menu.')
            if explicit_project_id is None:
                Log.info("No project specified while using the unmodified client.")
                print('Please ensure you specify a project id when creating the client'
                    ' in order to use your BigQuery account.')
            kwargs['client_info'] = set_kaggle_user_agent(kwargs.get('client_info'))
            return bq_client(*args, **kwargs)

    # Monkey patches BigQuery client creation to use proxy or user-connected GCP account.
    # Deprecated in favor of Kaggle.DataProxyClient().
    # TODO: Remove this once uses have migrated to that new interface.
    bq_client = bigquery.Client
    if (not has_been_monkeypatched(bigquery.Client)):
        bigquery.Client = lambda *args, **kwargs:  monkeypatch_bq(
            bq_client, *args, **kwargs)
    return bigquery

def monkeypatch_client(client_klass, kaggle_kernel_credentials):
    client_init = client_klass.__init__
    def patched_init(self, *args, **kwargs):
        specified_credentials = kwargs.get('credentials')
        if specified_credentials is None:
            Log.info("No credentials specified, using KaggleKernelCredentials.")
            kwargs['credentials'] = kaggle_kernel_credentials
        
        # TODO(vimota): Remove the exclusion of TablesClient once
        # the client has fixed the error:
        # `multiple values for keyword argument 'client_info'``
        from google.cloud import automl_v1beta1
        if (client_klass != automl_v1beta1.TablesClient):
            kwargs['client_info'] = set_kaggle_user_agent(kwargs.get('client_info'))


        return client_init(self, *args, **kwargs)

    if (not has_been_monkeypatched(client_klass.__init__)):
        client_klass.__init__ = patched_init

def set_kaggle_user_agent(client_info: ClientInfo):
    # Add kaggle client user agent in order to attribute usage.
    if client_info is None:
        client_info = ClientInfo(user_agent=KAGGLE_GCP_CLIENT_USER_AGENT)
    else:
        client_info.user_agent = KAGGLE_GCP_CLIENT_USER_AGENT
    return client_info

def init_gcs():
    is_user_secrets_token_set = "KAGGLE_USER_SECRETS_TOKEN" in os.environ
    from google.cloud import storage
    if not is_user_secrets_token_set:
        return storage

    from kaggle_gcp import get_integrations
    if not get_integrations().has_gcs():
        return storage

    from kaggle_secrets import GcpTarget
    from kaggle_gcp import KaggleKernelCredentials
    monkeypatch_client(
        storage.Client,
        KaggleKernelCredentials(target=GcpTarget.GCS))
    return storage

def init_automl():
    is_user_secrets_token_set = "KAGGLE_USER_SECRETS_TOKEN" in os.environ
    from google.cloud import automl_v1beta1 as automl
    if not is_user_secrets_token_set:
        return automl

    from kaggle_gcp import get_integrations
    if not get_integrations().has_automl():
        return automl

    from kaggle_secrets import GcpTarget
    from kaggle_gcp import KaggleKernelCredentials
    kaggle_kernel_credentials = KaggleKernelCredentials(target=GcpTarget.AUTOML)

    # The AutoML client library exposes 4 different client classes (AutoMlClient,
    # TablesClient, PredictionServiceClient and GcsClient), so patch each of them.
    # The same KaggleKernelCredentials are passed to all of them.
    monkeypatch_client(automl.AutoMlClient, kaggle_kernel_credentials)
    monkeypatch_client(automl.TablesClient, kaggle_kernel_credentials)
    monkeypatch_client(automl.PredictionServiceClient, kaggle_kernel_credentials)
    # TODO(markcollins): The GcsClient in the AutoML client library version
    # 0.5.0 doesn't handle credentials properly. I wrote PR:
    # https://github.com/googleapis/google-cloud-python/pull/9299
    # to address this issue. Add patching for GcsClient when we get a version of
    # the library that includes the fixes.
    return automl

def init():
    init_bigquery()
    init_gcs()
    init_automl()

# We need to initialize the monkeypatching of the client libraries
# here since there is a circular dependency between our import hook version
# google.cloud.* and kaggle_gcp. By calling init here, we guarantee
# that regardless of the original import that caused google.cloud.* to be
# loaded, the monkeypatching will be done.
init()
