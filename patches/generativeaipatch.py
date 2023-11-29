import wrapt
import os

@wrapt.when_imported('google.generativeai')
def post_import_logic(module):
    old_configure = module.configure
    def new_configure(*args, **kwargs):
        if ('default_metadata' in kwargs):
            default_metadata = kwargs['default_metadata']
        else:
            default_metadata = []
        kwargs['transport'] = 'rest' # Only support REST requests for now
        default_metadata.append(("x-kaggle-proxy-data", os.environ['KAGGLE_DATA_PROXY_TOKEN']))
        default_metadata.append(('x-kaggle-authorization', f'Bearer {os.environ['KAGGLE_USER_SECRETS_TOKEN']}'))
        kwargs['default_metadata'] = default_metadata
        if ('client_options' in kwargs):
            client_options = kwargs['client_options']
        else:
            client_options = {}
        client_options['api_endpoint'] = os.environ['KAGGLE_DATA_PROXY_URL'] + '/palmapi'
        kwargs['client_options'] = client_options
        old_configure(*args, **kwargs)
    module.configure = new_configure
    module.configure() # generativeai can use GOOGLE_API_KEY env variable, so make sure we have the other configs set
