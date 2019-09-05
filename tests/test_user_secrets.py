import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from test.support import EnvironmentVarGuard
from urllib.parse import urlparse
from datetime import datetime, timedelta
import mock

from google.auth.exceptions import DefaultCredentialsError
from google.cloud import bigquery
from kaggle_secrets import (_KAGGLE_URL_BASE_ENV_VAR_NAME,
                            _KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME,
                            CredentialError, GcpTarget, UserSecretsClient,
                            BackendError, ValidationError)

_TEST_JWT = 'test-secrets-key'


class UserSecretsHTTPHandler(BaseHTTPRequestHandler):

    def set_request(self):
        raise NotImplementedError()

    def get_response(self):
        raise NotImplementedError()

    def do_HEAD(s):
        s.send_response(200)

    def do_POST(s):
        s.set_request()
        s.send_response(200)
        s.send_header("Content-type", "application/json")
        s.end_headers()
        s.wfile.write(json.dumps(s.get_response()).encode("utf-8"))


class TestUserSecrets(unittest.TestCase):
    SERVER_ADDRESS = urlparse(os.getenv(_KAGGLE_URL_BASE_ENV_VAR_NAME, default="http://127.0.0.1:8001"))

    def _test_client(self, client_func, expected_path, expected_body, secret=None, success=True):
        _request = {}

        class AccessTokenHandler(UserSecretsHTTPHandler):

            def set_request(self):
                _request['path'] = self.path
                content_len = int(self.headers.get('Content-Length'))
                _request['body'] = json.loads(self.rfile.read(content_len))
                _request['headers'] = self.headers

            def get_response(self):
                if success:
                    return {'result': {'secret': secret, 'secretType': 'refreshToken', 'secretProvider': 'google', 'expiresInSeconds': 3600}, 'wasSuccessful': "true"}
                else:
                    return {'wasSuccessful': "false"}

        env = EnvironmentVarGuard()
        env.set(_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME, _TEST_JWT)
        with env:
            with HTTPServer((self.SERVER_ADDRESS.hostname, self.SERVER_ADDRESS.port), AccessTokenHandler) as httpd:
                threading.Thread(target=httpd.serve_forever).start()

                try:
                    client_func()
                finally:
                    httpd.shutdown()

                path, headers, body = _request['path'], _request['headers'], _request['body']
                self.assertEqual(
                    path,
                    expected_path,
                    msg="Fake server did not receive the right request from the UserSecrets client.")
                self.assertEqual(
                    body,
                    expected_body,
                    msg="Fake server did not receive the right body from the UserSecrets client.")

    def test_no_token_fails(self):
        env = EnvironmentVarGuard()
        env.unset(_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME)
        with env:
            with self.assertRaises(CredentialError):
                client = UserSecretsClient()

    def test_get_secret_succeeds(self):
        secret = '12345'

        def call_get_secret():
            client = UserSecretsClient()
            secret_response = client.get_secret("secret_label")
            self.assertEqual(secret_response, secret)
        self._test_client(call_get_secret,
                          '/requests/GetUserSecretByLabelRequest', {'Label': "secret_label", 'JWE': _TEST_JWT},
                          secret=secret)
    
    def test_get_secret_handles_unsuccessful(self):
        def call_get_secret():
            client = UserSecretsClient()
            with self.assertRaises(BackendError):
                secret_response = client.get_secret("secret_label")
        self._test_client(call_get_secret,
                          '/requests/GetUserSecretByLabelRequest', {'Label': "secret_label", 'JWE': _TEST_JWT},
                          success=False)

    def test_get_secret_validates_label(self):
        env = EnvironmentVarGuard()
        env.set(_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME, _TEST_JWT)
        with env:
            client = UserSecretsClient()
            with self.assertRaises(ValidationError):
                secret_response = client.get_secret("")
                          
    @mock.patch('kaggle_secrets.datetime')
    def test_get_access_token_succeeds(self, mock_dt):
        secret = '12345'
        now = datetime(1993, 4, 24)
        mock_dt.utcnow = mock.Mock(return_value=now)

        def call_get_bigquery_access_token():
            client = UserSecretsClient()
            secret_response = client.get_bigquery_access_token()
            self.assertEqual(secret_response, (secret, now + timedelta(seconds=3600)))
        def call_get_gcs_access_token():
            client = UserSecretsClient()
            secret_response = client._get_gcs_access_token()
            self.assertEqual(secret_response, (secret, now + timedelta(seconds=3600)))
        self._test_client(call_get_bigquery_access_token,
                          '/requests/GetUserSecretRequest', {'Target': GcpTarget.BIGQUERY.target, 'JWE': _TEST_JWT},
                          secret=secret)
        self._test_client(call_get_gcs_access_token,
                          '/requests/GetUserSecretRequest', {'Target': GcpTarget.GCS.target, 'JWE': _TEST_JWT},
                          secret=secret)

    def test_get_access_token_handles_unsuccessful(self):
        def call_get_access_token():
            client = UserSecretsClient()
            with self.assertRaises(BackendError):
                client.get_bigquery_access_token()
        self._test_client(call_get_access_token,
                          '/requests/GetUserSecretRequest', {'Target': GcpTarget.BIGQUERY.target, 'JWE': _TEST_JWT}, success=False)
