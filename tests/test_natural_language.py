import unittest
import inspect

from unittest.mock import Mock, patch

from kaggle_gcp import KaggleKernelCredentials, init_natural_language
from test.support import EnvironmentVarGuard
from google.cloud import language

def _make_credentials():
    import google.auth.credentials
    return Mock(spec=google.auth.credentials.Credentials)

class TestCloudNaturalLanguage(unittest.TestCase):
    class FakeClient:
        def __init__(self, credentials=None, client_info=None, **kwargs):
            self.credentials = credentials

            class FakeConnection():
                def __init__(self, user_agent):
                    self.user_agent = user_agent
            if (client_info is not None):
                self._connection = FakeConnection(client_info.user_agent)

    @patch("google.cloud.language.LanguageServiceClient", new=FakeClient)
    def test_default_credentials(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_natural_language()
            client = language.LanguageServiceClient()
            self.assertIsNotNone(client.credentials)
            self.assertIsInstance(client.credentials, KaggleKernelCredentials)

    @patch("google.cloud.language.LanguageServiceClient", new=FakeClient)
    def test_user_provided_credentials(self):
        credentials = _make_credentials()
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_natural_language()
            client = language.LanguageServiceClient(credentials=credentials)
            self.assertIsNotNone(client.credentials)
            self.assertNotIsInstance(client.credentials, KaggleKernelCredentials)


    def test_monkeypatching_succeed(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_natural_language()
            client = language.LanguageServiceClient.__init__
            self.assertTrue("kaggle_gcp" in inspect.getsourcefile(client))
   
    def test_monkeypatching_idempotent(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_natural_language()
            client1 = language.LanguageServiceClient.__init__
            init_natural_language()
            client2 = language.LanguageServiceClient.__init__
            self.assertEqual(client1, client2)
