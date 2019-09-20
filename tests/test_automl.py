import unittest

from unittest.mock import Mock

from kaggle_gcp import KaggleKernelCredentials, init_automl
from test.support import EnvironmentVarGuard
from google.cloud import storage, automl_v1beta1 as automl

def _make_credentials():
    import google.auth.credentials
    return Mock(spec=google.auth.credentials.Credentials)

class TestAutoMl(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(automl.auto_ml_client._GAPIC_LIBRARY_VERSION)
        version_parts = automl.auto_ml_client._GAPIC_LIBRARY_VERSION.split('.')
        version = float('.'.join(version_parts[0:2]));
        self.assertGreaterEqual(version, 0.5);

    def test_user_provided_credentials(self):
        credentials = _make_credentials()
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'AUTOML')
        with env:
            init_automl()
            client = automl.AutoMlClient(credentials=credentials)
            self.assertNotIsInstance(client._kaggle_credentials, KaggleKernelCredentials)
            self.assertIsNotNone(client._kaggle_credentials)


    def test_tables_gcs_client(self):
        # The GcsClient can't currently be monkeypatched for default
        # credentials because it requires a project which can't be set.
        # Verify that creating an automl.GcsClient given an actual
        # storage.Client sets the client properly.
        gcs_client = storage.Client(project="xyz", credentials=_make_credentials())
        tables_gcs_client = automl.GcsClient(client=gcs_client)
        self.assertIs(tables_gcs_client.client, gcs_client)

    def test_default_credentials_automl_enabled(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'AUTOML')
        with env:
            init_automl()
            automl_client = automl.AutoMlClient()
            self.assertIsNotNone(automl_client._kaggle_credentials)
            self.assertIsInstance(automl_client._kaggle_credentials, KaggleKernelCredentials)
            tables_client = automl.TablesClient()
            self.assertIsNotNone(automl_client._kaggle_credentials)
            self.assertIsInstance(automl_client._kaggle_credentials, KaggleKernelCredentials)
            prediction_client = automl.PredictionServiceClient()
            self.assertIsNotNone(automl_client._kaggle_credentials)
            self.assertIsInstance(automl_client._kaggle_credentials, KaggleKernelCredentials)

    def test_monkeypatching_idempotent(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'GCS')
        with env:
            client1 = automl.AutoMlClient.__init__
            init_automl()
            client2 = automl.AutoMlClient.__init__
            self.assertEqual(client1, client2)
