import unittest

import os
import tensorflow_gcs_config
from unittest.mock import patch
from test.support import EnvironmentVarGuard
from kaggle_secrets import UserSecretsClient

class TestTensorflowCredentials(unittest.TestCase):

    @patch('tensorflow_gcs_config.configure_gcs')
    def test_set_tensorflow_credential(self, mock_configure_gcs):
        credential = '{"client_id":"fake_client_id",' \
            '"client_secret":"fake_client_secret",' \
            '"refresh_token":"not a refresh token",' \
            '"type":"authorized_user"}'

        env = EnvironmentVarGuard()
        env.set('HOME', '/tmp')
        env.set('GOOGLE_APPLICATION_CREDENTIALS', '')

        # These need to be set to make UserSecretsClient happy, but aren't
        # pertinent to this test.
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'CLOUDAI')

        user_secrets = UserSecretsClient()
        user_secrets.set_tensorflow_credential(credential)

        credential_path = '/tmp/gcloud_credential.json'
        self.assertEqual(
            credential_path, os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
        with open(credential_path, 'r') as f:
          saved_cred = f.read()
          self.assertEqual(credential, saved_cred)

          mock_configure_gcs.assert_called_with(credentials=credential)
