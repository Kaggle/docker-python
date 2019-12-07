import unittest

from unittest.mock import Mock

from kaggle_gcp import KaggleKernelCredentials, init_gcs
from test.support import EnvironmentVarGuard
from google.cloud import storage

def _make_credentials():
    import google.auth.credentials
    return Mock(spec=google.auth.credentials.Credentials)

class TestStorage(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(storage.__version__)

    def test_ctr(self):
        credentials = _make_credentials()
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'GCS')
        with env:
            init_gcs()
            client = storage.Client(project="xyz", credentials=credentials)
            self.assertEqual(client.project, "xyz")
            self.assertNotIsInstance(client._credentials, KaggleKernelCredentials)
            self.assertIsNotNone(client._credentials)

    def test_annonymous_client(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'GCS')
        with env:
            init_gcs()
            anonymous = storage.Client.create_anonymous_client()
            self.assertIsNotNone(anonymous)

    def test_default_credentials_gcs_enabled(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'GCS')
        with env:
            init_gcs()
            client = storage.Client(project="xyz")
            self.assertIsInstance(client._credentials, KaggleKernelCredentials)
            self.assertTrue(client._connection.user_agent.startswith("kaggle-gcp-client/1.0"))
    
    def test_monkeypatching_idempotent(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'GCS')
        with env:
            client1 = storage.Client.__init__
            init_gcs()
            client2 = storage.Client.__init__
            self.assertEqual(client1, client2)
