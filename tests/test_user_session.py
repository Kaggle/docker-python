import json
import os
import threading
import unittest

from http.server import BaseHTTPRequestHandler, HTTPServer
from test.support import EnvironmentVarGuard
from urllib.parse import urlparse
from kaggle_session import UserSessionClient
from kaggle_web_client import (_KAGGLE_URL_BASE_ENV_VAR_NAME,
                            _KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME,
                            CredentialError, BackendError)

class UserSessionHTTPHandler(BaseHTTPRequestHandler):

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

class TestUserSessionClient(unittest.TestCase):
    SERVER_ADDRESS = urlparse(os.getenv(_KAGGLE_URL_BASE_ENV_VAR_NAME, default="http://127.0.0.1:8001"))
    TEST_JWT = 'test-secrets-key'

    def _test_client(self, client_func, expected_path, expected_body, source=None, success=True):
        _request = {}

        class GetKernelRunSourceForCaipHandler(UserSessionHTTPHandler):
            def set_request(self):
                _request['path'] = self.path
                content_len = int(self.headers.get('Content-Length'))
                _request['body'] = json.loads(self.rfile.read(content_len))
                _request['headers'] = self.headers
            
            def get_response(self):
                if success:
                    return {'result': {'source': source}, 'wasSuccessful': 'true'}
                return {'wasSuccessful': 'false'}
        
        env = EnvironmentVarGuard()
        env.set(_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME, self.TEST_JWT)
        with env:
            with HTTPServer((self.SERVER_ADDRESS.hostname, self.SERVER_ADDRESS.port), GetKernelRunSourceForCaipHandler) as httpd:
                threading.Thread(target=httpd.serve_forever).start()

                try:
                    client_func()
                finally:
                    httpd.shutdown()
                
                path, headers, body = _request['path'], _request['headers'], _request['body']
                self.assertEqual(
                    path,
                    expected_path,
                    msg="Fake server did not receive the right request from UserSessionClient.")
                self.assertEqual(
                    body,
                    expected_body,
                    msg="Fake server did not receive the right body from UserSessionClient.")

    def test_no_token_fails(self):
        env = EnvironmentVarGuard()
        env.unset(_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME)
        with env:
            with self.assertRaises(CredentialError):
                client = UserSessionClient()
    
    def test_get_exportable_ipynb_succeeds(self):
        source = "import foo"

        def call_get_ipynb():
            client = UserSessionClient()
            response = client.get_exportable_ipynb()
            self.assertEqual(source, response['source'])

        self._test_client(
            call_get_ipynb,
            '/requests/GetKernelRunSourceForCaipRequest',
            {'UseDraft': True},
            source=source,
            success=True)

    def test_get_exportable_ipynb_fails(self):
        def call_get_ipynb():
            client = UserSessionClient()
            with self.assertRaises(BackendError):
                client.get_exportable_ipynb()

        self._test_client(
            call_get_ipynb,
            '/requests/GetKernelRunSourceForCaipRequest',
            {'UseDraft': True},
            success=False)