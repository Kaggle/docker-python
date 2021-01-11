import unittest
import inspect

from unittest.mock import Mock, patch

from kaggle_gcp import KaggleKernelCredentials, init_video_intelligence
from test.support import EnvironmentVarGuard
from google.cloud import videointelligence

def _make_credentials():
    import google.auth.credentials
    return Mock(spec=google.auth.credentials.Credentials)

class TestCloudVideoIntelligence(unittest.TestCase):
    class FakeClient:
        def __init__(self, credentials=None, client_info=None, **kwargs):
            self.credentials = credentials

            class FakeConnection():
                def __init__(self, user_agent):
                    self.user_agent = user_agent
            if (client_info is not None):
                self._connection = FakeConnection(client_info.user_agent)
 
    @patch("google.cloud.videointelligence.VideoIntelligenceServiceClient", new=FakeClient)
    def test_default_credentials(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_video_intelligence()
            client = videointelligence.VideoIntelligenceServiceClient()
            self.assertIsNotNone(client.credentials)
            self.assertIsInstance(client.credentials, KaggleKernelCredentials)

    @patch("google.cloud.videointelligence.VideoIntelligenceServiceClient", new=FakeClient)
    def test_user_provided_credentials(self):
        credentials = _make_credentials()
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_video_intelligence()
            client = videointelligence.VideoIntelligenceServiceClient(credentials=credentials)
            self.assertNotIsInstance(client.credentials, KaggleKernelCredentials)
            self.assertIsNotNone(client.credentials)

    def test_monkeypatching_succeed(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_video_intelligence()
            client = videointelligence.VideoIntelligenceServiceClient.__init__
            self.assertTrue("kaggle_gcp" in inspect.getsourcefile(client))

    def test_monkeypatching_idempotent(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            init_video_intelligence()
            client1 = videointelligence.VideoIntelligenceServiceClient.__init__
            init_video_intelligence()
            client2 = videointelligence.VideoIntelligenceServiceClient.__init__
            self.assertEqual(client1, client2)
