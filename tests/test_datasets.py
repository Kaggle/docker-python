import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from test.support import EnvironmentVarGuard
from urllib.parse import urlparse

from kaggle_secrets import (_KAGGLE_URL_BASE_ENV_VAR_NAME,
                            _KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME,
                            CredentialError, BackendError, ValidationError)
from kaggle_web_client import KaggleWebClient
from kaggle_datasets import KaggleDatasets, _KAGGLE_TPU_NAME_ENV_VAR_NAME

_TEST_JWT = 'test-secrets-key'

_TPU_GCS_BUCKET = 'gs://kds-tpu-ea1971a458ffd4cd51389e7574c022ecc0a82bb1b52ccef08c8a'
_AUTOML_GCS_BUCKET = 'gs://kds-automl-ea1971a458ffd4cd51389e7574c022ecc0a82bb1b52ccef08c8a'

class GcsDatasetsHTTPHandler(BaseHTTPRequestHandler):

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


class TestDatasets(unittest.TestCase):
    SERVER_ADDRESS = urlparse(os.getenv(_KAGGLE_URL_BASE_ENV_VAR_NAME, default="http://127.0.0.1:8001"))

    def _test_client(self, client_func, expected_path, expected_body, is_tpu=True, success=True):
        _request = {}

        class GetGcsPathHandler(GcsDatasetsHTTPHandler):

            def set_request(self):
                _request['path'] = self.path
                content_len = int(self.headers.get('Content-Length'))
                _request['body'] = json.loads(self.rfile.read(content_len))
                _request['headers'] = self.headers

            def get_response(self):
                if success:
                    gcs_path = _TPU_GCS_BUCKET if is_tpu else _AUTOML_GCS_BUCKET
                    return {'result': {
                        'destinationBucket': gcs_path,
                        'destinationPath': None}, 'wasSuccessful': "true"}
                else:
                    return {'wasSuccessful': "false"}

        env = EnvironmentVarGuard()
        env.set(_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME, _TEST_JWT)
        if is_tpu:
          env.set(_KAGGLE_TPU_NAME_ENV_VAR_NAME, 'FAKE_TPU')
        with env:
            with HTTPServer((self.SERVER_ADDRESS.hostname, self.SERVER_ADDRESS.port), GetGcsPathHandler) as httpd:
                threading.Thread(target=httpd.serve_forever).start()

                try:
                    client_func()
                finally:
                    httpd.shutdown()

                path, headers, body = _request['path'], _request['headers'], _request['body']
                self.assertEqual(
                    path,
                    expected_path,
                    msg="Fake server did not receive the right request from the KaggleDatasets client.")
                self.assertEqual(
                    body,
                    expected_body,
                    msg="Fake server did not receive the right body from the KaggleDatasets client.")
                self.assertIn('Content-Type', headers.keys(),
                    msg="Fake server did not receive a Content-Type header from the KaggleDatasets client.")
                self.assertEqual('application/json', headers.get('Content-Type'),
                    msg="Fake server did not receive an application/json content type header from the KaggleDatasets client.")
                self.assertIn('Authorization', headers.keys(),
                    msg="Fake server did not receive an Authorization header from the KaggleDatasets client.")
                self.assertEqual(f'Bearer {_TEST_JWT}', headers.get('Authorization'),
                    msg="Fake server did not receive the right Authorization header from the KaggleDatasets client.")

    def test_no_token_fails(self):
        env = EnvironmentVarGuard()
        env.unset(_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME)
        with env:
            with self.assertRaises(CredentialError):
                client = KaggleDatasets()

    def test_get_gcs_path_tpu_succeeds(self):
        def call_get_gcs_path():
            client = KaggleDatasets()
            gcs_path = client.get_gcs_path()
            self.assertEqual(gcs_path, _TPU_GCS_BUCKET)
        self._test_client(call_get_gcs_path,
                          '/requests/CopyDatasetVersionToKnownGcsBucketRequest',
                          {'MountSlug': None, 'IntegrationType': 2, 'JWE': _TEST_JWT},
                          is_tpu=True)

    def test_get_gcs_path_automl_succeeds(self):
        def call_get_gcs_path():
            client = KaggleDatasets()
            gcs_path = client.get_gcs_path()
            self.assertEqual(gcs_path, _AUTOML_GCS_BUCKET)
        self._test_client(call_get_gcs_path,
                          '/requests/CopyDatasetVersionToKnownGcsBucketRequest',
                          {'MountSlug': None, 'IntegrationType': 1, 'JWE': _TEST_JWT},
                          is_tpu=False)

    def test_get_gcs_path_handles_unsuccessful(self):
        def call_get_gcs_path():
            client = KaggleDatasets()
            with self.assertRaises(BackendError):
                gcs_path = client.get_gcs_path()
        self._test_client(call_get_gcs_path,
                          '/requests/CopyDatasetVersionToKnownGcsBucketRequest',
                          {'MountSlug': None, 'IntegrationType': 2, 'JWE': _TEST_JWT},
                          is_tpu=True,
                          success=False)
