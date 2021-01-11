import unittest
import inspect

from unittest.mock import Mock, patch

from kaggle_gcp import KaggleKernelCredentials, KaggleKernelWithProjetCredentials, init_translation_v2, init_translation_v3
from test.support import EnvironmentVarGuard
from google.api_core import client_options
from google.cloud import translate, translate_v2

def _make_credentials():
    import google.auth.credentials
    return Mock(spec=google.auth.credentials.Credentials)

class TestCloudTranslation(unittest.TestCase):
    class FakeClient:
        def __init__(self, credentials=None, client_info=None, client_options=None, **kwargs):
            self.credentials = credentials
            self.client_options = client_options

            class FakeConnection():
                def __init__(self, user_agent):
                    self.user_agent = user_agent
            if (client_info is not None):
                self._connection = FakeConnection(client_info.user_agent)

    @patch("google.cloud.translate_v2.Client", new=FakeClient)
    def test_default_credentials_v2(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_translation_v2()
            client = translate_v2.Client()
            self.assertIsNotNone(client.credentials)
            self.assertIsInstance(client.credentials, KaggleKernelCredentials)


    @patch("google.cloud.translate_v2.Client", new=FakeClient)
    def test_user_provided_credentials_v2(self):
        credentials = _make_credentials()
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_translation_v2()
            client = translate_v2.Client(credentials=credentials)
            self.assertIsNotNone(client.credentials)
            self.assertNotIsInstance(client.credentials, KaggleKernelCredentials)

    @patch("google.cloud.translate.TranslationServiceClient", new=FakeClient)
    def test_default_credentials_v3(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_translation_v3()
            client = translate.TranslationServiceClient()
            self.assertIsNotNone(client.credentials)
            self.assertIsInstance(client.credentials, KaggleKernelCredentials)


    @patch("google.cloud.translate.TranslationServiceClient", new=FakeClient)
    def test_user_provided_credentials_v3(self):
        credentials = _make_credentials()
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_translation_v3()
            client = translate.TranslationServiceClient(credentials=credentials)
            self.assertIsNotNone(client.credentials)
            self.assertNotIsInstance(client.credentials, KaggleKernelCredentials)


    def test_monkeypatching_succeed(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_translation_v2()
            init_translation_v3()
            # Translation V2
            client2 = translate_v2.Client.__init__
            self.assertTrue("kaggle_gcp" in inspect.getsourcefile(client2))
            # Translation V3
            client3 = translate.TranslationServiceClient.__init__
            self.assertTrue("kaggle_gcp" in inspect.getsourcefile(client3))

    def test_monkeypatching_idempotent(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_translation_v2()
            init_translation_v3()
            # Translation V2
            client2_1 = translate_v2.client.Client.__init__
            # Translation V3
            client3_1 = translate.TranslationServiceClient.__init__

            init_translation_v2()
            init_translation_v3()

            client2_2 = translate_v2.Client.__init__
            client3_2 = translate.TranslationServiceClient.__init__
            self.assertEqual(client2_1, client2_2)
            self.assertEqual(client3_1, client3_2)

    @patch("google.cloud.translate.TranslationServiceClient", new=FakeClient)
    def test_client_credential_uniqueness_v3(self):
        """
        Client instance must use unique KaggleKernelWithProjetCredentials with quota_project_id
        when client_options.quota_project_id provided. (even if quota_project_id is same)
        """
        credentials = _make_credentials()
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_translation_v3()
            client1 = translate.TranslationServiceClient()
            client2 = translate.TranslationServiceClient(client_options=client_options.ClientOptions(quota_project_id="_doesn't_matter"))
            client3 = translate.TranslationServiceClient(client_options=client_options.ClientOptions(quota_project_id="_doesn't_matter2"))
            self.assertIsNotNone(client1.credentials)
            self.assertIsNotNone(client2.credentials)
            self.assertIsNotNone(client3.credentials)
            self.assertIsInstance(client2.credentials, KaggleKernelWithProjetCredentials)
            self.assertIsInstance(client3.credentials, KaggleKernelWithProjetCredentials)
            self.assertNotEqual(client1.credentials, client2.credentials)
            self.assertNotEqual(client2.credentials, client3.credentials)
