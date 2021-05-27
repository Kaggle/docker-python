import os
import inspect
from google.auth import credentials, environment_vars
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
            Log.error(f"Unknown integration target: {integration.upper()}")
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

    def has_cloudai(self):
        return GcpTarget.CLOUDAI in self.integrations or \
            GcpTarget.AUTOML in self.integrations

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
            elif self.target == GcpTarget.CLOUDAI:
                self.token, self.expiry = client._get_cloudai_access_token()
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

class KaggleKernelWithProjetCredentials(KaggleKernelCredentials):
    """ Wrapper Kaggle Credentials with quota_project_id.
    """
    def __init__(self, parentCredential=None, quota_project_id=None):
        super().__init__(target=parentCredential.target)
        self._quota_project_id=quota_project_id

class _DataProxyConnection(Connection):
    """Custom Connection class used to proxy the BigQuery client to Kaggle's data proxy."""

    def __init__(self, client, **kwargs):
        super().__init__(client, **kwargs)
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
        default_api_endpoint = os.getenv("KAGGLE_DATA_PROXY_URL")
        anon_credentials = credentials.AnonymousCredentials()
        anon_credentials.refresh = lambda *args: None
        super().__init__(
            project=data_proxy_project, credentials=anon_credentials, *args, **kwargs
        )
        # TODO: Remove this once https://github.com/googleapis/google-cloud-python/issues/7122 is implemented.
        self._connection = _DataProxyConnection(self, api_endpoint=default_api_endpoint)

def has_been_monkeypatched(method):
    return "kaggle_gcp" in inspect.getsourcefile(method)

def is_user_secrets_token_set():
    return "KAGGLE_USER_SECRETS_TOKEN" in os.environ

def is_proxy_token_set():
    return "KAGGLE_DATA_PROXY_TOKEN" in os.environ

def init_bigquery():
    from google.cloud import bigquery

    if not (is_proxy_token_set() or is_user_secrets_token_set()):
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

# Monkey patch for aiplatform init 
# eg
# from google.cloud import aiplatform
# aiplatform.init(args)
def monkeypatch_aiplatform_init(aiplatform_klass, kaggle_kernel_credentials):
    aiplatform_init = aiplatform_klass.init
    def patched_init(*args, **kwargs):
        specified_credentials = kwargs.get('credentials')
        if specified_credentials is None:
            Log.info("No credentials specified, using KaggleKernelCredentials.")
            kwargs['credentials'] = kaggle_kernel_credentials
        return aiplatform_init(*args, **kwargs)

    if (not has_been_monkeypatched(aiplatform_klass.init)):
        aiplatform_klass.init = patched_init
        Log.info("aiplatform.init patched")

def monkeypatch_client(client_klass, kaggle_kernel_credentials):
    client_init = client_klass.__init__
    def patched_init(self, *args, **kwargs):
        specified_credentials = kwargs.get('credentials')
        if specified_credentials is None:
            Log.info("No credentials specified, using KaggleKernelCredentials.")
            # Some GCP services demand the billing and target project must be the same.
            # To avoid using default service account based credential as caller credential
            # user need to provide ClientOptions with quota_project_id:
            # srv.Client(client_options=client_options.ClientOptions(quota_project_id="YOUR PROJECT"))
            client_options=kwargs.get('client_options')
            if client_options != None and client_options.quota_project_id != None:
                kwargs['credentials'] = KaggleKernelWithProjetCredentials(
                    parentCredential = kaggle_kernel_credentials,
                    quota_project_id = client_options.quota_project_id)
            else:
                kwargs['credentials'] = kaggle_kernel_credentials

        kwargs['client_info'] = set_kaggle_user_agent(kwargs.get('client_info'))
        return client_init(self, *args, **kwargs)

    if (not has_been_monkeypatched(client_klass.__init__)):
        client_klass.__init__ = patched_init
        Log.info(f"Client patched: {client_klass}")

def set_kaggle_user_agent(client_info: ClientInfo):
    # Add kaggle client user agent in order to attribute usage.
    if client_info is None:
        client_info = ClientInfo(user_agent=KAGGLE_GCP_CLIENT_USER_AGENT)
    else:
        client_info.user_agent = KAGGLE_GCP_CLIENT_USER_AGENT
    return client_info

def init_gcs():
    from google.cloud import storage
    if not is_user_secrets_token_set():
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
    from google.cloud import automl, automl_v1beta1
    if not is_user_secrets_token_set():
        return

    from kaggle_gcp import get_integrations
    if not get_integrations().has_cloudai():
        return

    from kaggle_secrets import GcpTarget
    from kaggle_gcp import KaggleKernelCredentials
    kaggle_kernel_credentials = KaggleKernelCredentials(target=GcpTarget.CLOUDAI)

    # Patch the 2 GA clients: AutoMlClient and PreditionServiceClient
    monkeypatch_client(automl.AutoMlClient, kaggle_kernel_credentials)
    monkeypatch_client(automl.PredictionServiceClient, kaggle_kernel_credentials)

    # The AutoML client library exposes 3 different client classes (AutoMlClient,
    # TablesClient, PredictionServiceClient), so patch each of them.
    # The same KaggleKernelCredentials are passed to all of them.
    # The GcsClient class is only used internally by TablesClient.

    # The beta version of the clients that are now GA are included here for now.
    # They are deprecated and will be removed by 1 May 2020.
    monkeypatch_client(automl_v1beta1.AutoMlClient, kaggle_kernel_credentials)
    monkeypatch_client(automl_v1beta1.PredictionServiceClient, kaggle_kernel_credentials)

    # The TablesClient is still in beta, so this will not be deprecated until
    # the TablesClient is GA.
    monkeypatch_client(automl_v1beta1.TablesClient, kaggle_kernel_credentials)

def init_translation_v2():
    from google.cloud import translate_v2
    if not is_user_secrets_token_set():
        return translate_v2

    from kaggle_gcp import get_integrations
    if not get_integrations().has_cloudai():
        return translate_v2
    from kaggle_secrets import GcpTarget
    kernel_credentials = KaggleKernelCredentials(target=GcpTarget.CLOUDAI)
    monkeypatch_client(translate_v2.Client, kernel_credentials)
    return translate_v2

def init_translation_v3():
    # Translate v3 exposes different client than translate v2.
    from google.cloud import translate_v3
    if not is_user_secrets_token_set():
        return translate_v3

    from kaggle_gcp import get_integrations
    if not get_integrations().has_cloudai():
        return translate_v3
    from kaggle_secrets import GcpTarget
    kernel_credentials = KaggleKernelCredentials(target=GcpTarget.CLOUDAI)
    monkeypatch_client(translate_v3.TranslationServiceClient, kernel_credentials)
    return translate_v3

def init_natural_language():
    from google.cloud import language
    if not is_user_secrets_token_set():
        return language

    from kaggle_gcp import get_integrations
    if not get_integrations().has_cloudai():
        return language

    from kaggle_secrets import GcpTarget
    kernel_credentials = KaggleKernelCredentials(target=GcpTarget.CLOUDAI)
    monkeypatch_client(language.LanguageServiceClient, kernel_credentials)    
    monkeypatch_client(language.LanguageServiceAsyncClient, kernel_credentials)
    return language

def init_ucaip():
    from google.cloud import aiplatform
    if not is_user_secrets_token_set():
        return

    from kaggle_gcp import get_integrations
    if not get_integrations().has_cloudai():
        return

    from kaggle_secrets import GcpTarget
    from kaggle_gcp import KaggleKernelCredentials
    kaggle_kernel_credentials = KaggleKernelCredentials(target=GcpTarget.CLOUDAI)

    # Patch the ucaip init method, this flows down to all ucaip services
    monkeypatch_aiplatform_init(aiplatform, kaggle_kernel_credentials)

def init_video_intelligence():
    from google.cloud import videointelligence
    if not is_user_secrets_token_set():
        return videointelligence

    from kaggle_gcp import get_integrations
    if not get_integrations().has_cloudai():
        return videointelligence

    from kaggle_secrets import GcpTarget
    kernel_credentials = KaggleKernelCredentials(target=GcpTarget.CLOUDAI)
    monkeypatch_client(
        videointelligence.VideoIntelligenceServiceClient,
        kernel_credentials)
    monkeypatch_client(
        videointelligence.VideoIntelligenceServiceAsyncClient,
        kernel_credentials)
    return videointelligence

def init_vision():
    from google.cloud import vision
    if not is_user_secrets_token_set():
        return vision

    from kaggle_gcp import get_integrations
    if not get_integrations().has_cloudai():
        return vision

    from kaggle_secrets import GcpTarget
    kernel_credentials = KaggleKernelCredentials(target=GcpTarget.CLOUDAI)
    monkeypatch_client(vision.ImageAnnotatorClient, kernel_credentials)
    monkeypatch_client(vision.ImageAnnotatorAsyncClient, kernel_credentials)
    return vision

def init():
    init_bigquery()
    init_gcs()
    init_automl()
    init_translation_v2()
    init_translation_v3()
    init_natural_language()
    init_video_intelligence()
    init_vision()
    init_ucaip()

# We need to initialize the monkeypatching of the client libraries
# here since there is a circular dependency between our import hook version
# google.cloud.* and kaggle_gcp. By calling init here, we guarantee
# that regardless of the original import that caused google.cloud.* to be
# loaded, the monkeypatching will be done.
init()
