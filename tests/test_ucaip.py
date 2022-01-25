import unittest

from unittest.mock import Mock

from kaggle_gcp import KaggleKernelCredentials, init_ucaip
from test.support import EnvironmentVarGuard

def _make_credentials():
    import google.auth.credentials
    return Mock(spec=google.auth.credentials.Credentials)

class TestUcaip(unittest.TestCase):

    def test_user_provided_credentials(self):
        credentials = _make_credentials()
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')
        with env:
            from google.cloud import aiplatform
            init_ucaip()
            aiplatform.init(credentials=credentials)
            self.assertNotIsInstance(aiplatform.initializer.global_config.credentials, KaggleKernelCredentials)
            self.assertIsNotNone(aiplatform.initializer.global_config.credentials)