import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from test.support import EnvironmentVarGuard
from urllib.parse import urlparse

from google.auth.exceptions import DefaultCredentialsError
from google.cloud import bigquery
from kaggle_secrets import (_KAGGLE_URL_BASE_ENV_VAR_NAME,
                            _KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME,
                            CredentialError, UserSecretsClient)

_TEST_JWT = 'test-secrets-key'


class UserSecretsHTTPHandler(BaseHTTPRequestHandler):

    def set_request(self):
        raise NotImplementedError()
    
    def get_response(self):
        raise NotImplementedError()

    def do_HEAD(s):
        s.send_response(200)

    def do_GET(s):
        s.set_request()
        s.send_response(200)
        s.send_header("Content-type", "application/json")
        s.end_headers()
        s.wfile.write(json.dumps(s.get_response()).encode("utf-8"))


class TestUserSecrets(unittest.TestCase):
    server_address = urlparse(os.getenv(_KAGGLE_URL_BASE_ENV_VAR_NAME))

    def _test_client(self, client_func, expected_path, secret):
        _request = {}

        class AccessTokenHandler(UserSecretsHTTPHandler):
            def set_request(self):
                _request['path'] = self.path
                _request['headers'] = self.headers
            def get_response(self):
                return {"Secret": secret}

        env = EnvironmentVarGuard()
        env.set(_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME, _TEST_JWT)
        with env:
            with HTTPServer((self.server_address.hostname, self.server_address.port), AccessTokenHandler) as httpd:
                threading.Thread(target=httpd.serve_forever).start()

                try:
                    client_func()
                finally:
                    httpd.shutdown()

                self.assertEqual(
                    _request['path'], expected_path, msg="Fake server did not receive the right request from the UserSecrets client.")
                self.assertTrue(
                    any(
                        k for k in _request['headers'] if k == "Authorization" and _request['headers'][k] == f'Bearer {_TEST_JWT}'), msg="Authorization header was missing from the UserSecrets request.")

    def test_no_token_fails(self):
        env = EnvironmentVarGuard()
        env.unset(_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME)
        with env:
            with self.assertRaises(CredentialError):
                client = UserSecretsClient()

    def test_get_access_token_succeeds(self):
        secret = '12345'
        def call_get_access_token():
            client = UserSecretsClient()
            secret_response = client.getBigQueryAccessToken()
            self.assertEqual(secret_response, secret)
        self._test_client(call_get_access_token, '/requests/GetUserSecretRequest?Purpose=1', secret)

    def test_get_user_secret_succeeds(self):
        secret = '5678'
        def call_get_access_token():
            client = UserSecretsClient()
            secret_response = client.getUserSecret('MY_SECRET')
            self.assertEqual(secret_response, secret)
        self._test_client(call_get_access_token, '/requests/GetUserSecretRequest?SecretLabel=MY_SECRET', secret)
