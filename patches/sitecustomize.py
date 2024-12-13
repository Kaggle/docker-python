import os

from log import Log

import sys
import importlib.abc
import importlib
import importlib.machinery

import wrapt

class GcpModuleFinder(importlib.abc.MetaPathFinder):
    _MODULES = [
        'google.cloud.bigquery',
        'google.cloud.storage',
        'google.cloud.automl_v1beta1',
        'google.cloud.translate',
        'google.cloud.translate_v2',
        'google.cloud.translate_v3',
        'google.cloud.language',
        'google.cloud.language_v1',
        'google.cloud.videointelligence',
        'google.cloud.videointelligence_v1',
        'google.cloud.vision',
        'google.cloud.vision_v1',
    ]
    _KAGGLE_GCP_PATH = 'kaggle_gcp.py'
    def __init__(self):
        pass

    def _is_called_from_kaggle_gcp(self):
        import inspect
        for frame in inspect.stack():
            if os.path.basename(frame.filename) == self._KAGGLE_GCP_PATH:
                return True
        return False

    def find_spec(self, fullname, path, target=None):
        if fullname in self._MODULES:
            # If being called from kaggle_gcp, don't return our
            # monkeypatched module to avoid circular dependency,
            # since we call kaggle_gcp to load the module.
            if self._is_called_from_kaggle_gcp():
                return None
            return importlib.machinery.ModuleSpec(fullname, GcpModuleLoader())


class GcpModuleLoader(importlib.abc.Loader):
    def __init__(self):
        pass

    def create_module(self, spec):
        """Create the gcp module from the spec.
        """
        import kaggle_gcp
        _LOADERS = {
            'google.cloud.bigquery': kaggle_gcp.init_bigquery,
            'google.cloud.storage': kaggle_gcp.init_gcs,
            'google.cloud.automl_v1beta1': kaggle_gcp.init_automl,
            'google.cloud.translate': kaggle_gcp.init_translation_v3,
            'google.cloud.translate_v2': kaggle_gcp.init_translation_v2,
            'google.cloud.translate_v3': kaggle_gcp.init_translation_v3,
            'google.cloud.language': kaggle_gcp.init_natural_language,
            'google.cloud.language_v1': kaggle_gcp.init_natural_language,
            'google.cloud.videointelligence': kaggle_gcp.init_video_intelligence,
            'google.cloud.videointelligence_v1': kaggle_gcp.init_video_intelligence,
            'google.cloud.vision': kaggle_gcp.init_vision,
            'google.cloud.vision_v1': kaggle_gcp.init_vision
        }
        monkeypatch_gcp_module = _LOADERS[spec.name]()
        return monkeypatch_gcp_module

    def exec_module(self, module):
        pass

if not hasattr(sys, 'frozen'):
    sys.meta_path.insert(0, GcpModuleFinder())

@wrapt.when_imported('google.generativeai')
def post_import_logic(module):
    if os.getenv('KAGGLE_DISABLE_GOOGLE_GENERATIVE_AI_INTEGRATION') != None:
      return
    if (os.getenv('KAGGLE_DATA_PROXY_TOKEN') == None or 
       os.getenv('KAGGLE_USER_SECRETS_TOKEN') == None or
       (os.getenv('KAGGLE_DATA_PROXY_URL') == None and
       os.getenv('KAGGLE_GRPC_DATA_PROXY_URL') == None)):
      return

    old_configure = module.configure

    def new_configure(*args, **kwargs):
        if ('default_metadata' in kwargs):
            default_metadata = kwargs['default_metadata']
        else:
            default_metadata = []
        default_metadata.append(("x-kaggle-proxy-data", os.environ['KAGGLE_DATA_PROXY_TOKEN']))
        user_secrets_token = os.environ['KAGGLE_USER_SECRETS_TOKEN']
        default_metadata.append(('x-kaggle-authorization', f'Bearer {user_secrets_token}'))
        kwargs['default_metadata'] = default_metadata

        if ('client_options' in kwargs):
            client_options = kwargs['client_options']
        else:
            client_options = {}

        if os.getenv('KAGGLE_GOOGLE_GENERATIVE_AI_USE_REST_ONLY') != None:
            kwargs['transport'] = 'rest'
            
        if 'transport' in kwargs and kwargs['transport'] == 'rest':
            client_options['api_endpoint'] = os.environ['KAGGLE_DATA_PROXY_URL']
            client_options['api_endpoint'] += '/palmapi'
        else:
            client_options['api_endpoint'] = os.environ['KAGGLE_GRPC_DATA_PROXY_URL']
        kwargs['client_options'] = client_options

        old_configure(*args, **kwargs)

    module.configure = new_configure
    module.configure() # generativeai can use GOOGLE_API_KEY env variable, so make sure we have the other configs set

@wrapt.when_imported('google.genai')
def post_genai_import_logic(module):
    if os.getenv('KAGGLE_DISABLE_GOOGLE_GENERATIVE_AI_INTEGRATION'):
        return

    if not (os.getenv('KAGGLE_DATA_PROXY_TOKEN') and
            os.getenv('KAGGLE_USER_SECRETS_TOKEN') and
            os.getenv('KAGGLE_DATA_PROXY_URL')):
        return
    @wrapt.patch_function_wrapper(module, 'Client.__init__')
    def init_wrapper(wrapped, instance, args, kwargs):
        # Don't want to forward requests that are to Vertex AI, debug mode, or have their own http_options specified
        # Thus, if the client constructor contains any params other than api_key, we don't set up forwarding
        if any(value is not None for key, value in kwargs.items() if key != 'api_key'):
            return wrapped(*args, **kwargs)

        default_metadata = {
            "x-kaggle-proxy-data": os.environ['KAGGLE_DATA_PROXY_TOKEN'],
            'x-kaggle-authorization': f"Bearer {os.environ['KAGGLE_USER_SECRETS_TOKEN']}"
        }
        http_options = {
            'base_url': os.getenv('KAGGLE_DATA_PROXY_URL') + '/palmapi/',
            'headers': default_metadata
        }
        kwargs['http_options'] = http_options
        return wrapped(*args, **kwargs)
