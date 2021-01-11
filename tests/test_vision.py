import unittest
import inspect

from unittest.mock import Mock, patch

from kaggle_gcp import KaggleKernelCredentials, init_vision
from test.support import EnvironmentVarGuard
from google.cloud import vision

def _make_credentials():
    import google.auth.credentials
    return Mock(spec=google.auth.credentials.Credentials)

class TestCloudVision(unittest.TestCase):
    class FakeClient:
        def __init__(self, credentials=None, client_info=None, **kwargs):
            self.credentials = credentials

            class FakeConnection():
                def __init__(self, user_agent):
                    self.user_agent = user_agent
            if (client_info is not None):
                self._connection = FakeConnection(client_info.user_agent)

    @patch("google.cloud.vision.ImageAnnotatorClient", new=FakeClient)
    def test_default_credentials(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_vision()
            client = vision.ImageAnnotatorClient()
            self.assertIsNotNone(client.credentials)
            self.assertIsInstance(client.credentials, KaggleKernelCredentials)

    @patch("google.cloud.vision.ImageAnnotatorClient", new=FakeClient)
    def test_user_provided_credentials(self):
        credentials = _make_credentials()
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_vision()
            client = vision.ImageAnnotatorClient(credentials=credentials)
            self.assertNotIsInstance(client.credentials, KaggleKernelCredentials)
            self.assertIsNotNone(client.credentials)

    def test_monkeypatching_succeed(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_vision()
            client = vision.ImageAnnotatorClient.__init__
            self.assertTrue("kaggle_gcp" in inspect.getsourcefile(client))

    def test_monkeypatching_idempotent(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_vision()
            client1 = vision.ImageAnnotatorClient.__init__
            init_vision()
            client2 = vision.ImageAnnotatorClient.__init__
            self.assertEqual(client1, client2)
