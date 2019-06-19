import unittest
import os
import json
from unittest.mock import patch
import threading
from test.support import EnvironmentVarGuard
from urllib.parse import urlparse

from http.server import BaseHTTPRequestHandler, HTTPServer

from google.cloud import bigquery
from google.auth.exceptions import DefaultCredentialsError
from google.cloud.bigquery._http import Connection
from kaggle_gcp import KaggleKernelCredentials, PublicBigqueryClient
import kaggle_secrets


class TestBigQuery(unittest.TestCase):

    API_BASE_URL = "http://127.0.0.1:2121"
    def _test_proxy(self, client, should_use_proxy):
        class HTTPHandler(BaseHTTPRequestHandler):
            called = False
            bearer_header_found = False
            proxy_header_found = False

            def do_HEAD(self):
                self.send_response(200)

            def do_GET(self):
                HTTPHandler.called = True
                HTTPHandler.proxy_header_found = any(
                    k for k in self.headers if k == "X-KAGGLE-PROXY-DATA" and self.headers[k] == "test-key")
                HTTPHandler.bearer_header_found = any(
                    k for k in self.headers if k == "authorization" and self.headers[k] == "Bearer secret")
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                sample_dataset = {
                    "id": "bigqueryproject:datasetname",
                    "datasetReference": {
                        "datasetId": "datasetname",
                        "projectId": "bigqueryproject"
                    }
                }
                self.wfile.write(json.dumps({"kind": "bigquery#datasetList", "datasets": [sample_dataset]}).encode("utf-8"))

        server_address = urlparse(os.getenv('KAGGLE_DATA_PROXY_URL') if should_use_proxy else self.API_BASE_URL)
        with HTTPServer((server_address.hostname, server_address.port), HTTPHandler) as httpd:
            threading.Thread(target=httpd.serve_forever).start()

            for dataset in client.list_datasets():
                self.assertEquals(dataset.dataset_id, "datasetname")    
            
            httpd.shutdown()
            self.assertTrue(
                    HTTPHandler.called, msg="Fake server was not called from the BQ client, but should have been.")
            if should_use_proxy:
                self.assertFalse(
                    HTTPHandler.bearer_header_found, msg="authorization header was included in the BQ proxy request.")
                self.assertTrue(
                    HTTPHandler.proxy_header_found, msg="X-KAGGLE-PROXY-DATA header was missing from the BQ proxy request.")
            else:
                self.assertFalse(
                    HTTPHandler.proxy_header_found, msg="X-KAGGLE-PROXY-DATA header was included in the BQ request.")
                self.assertTrue(
                    HTTPHandler.bearer_header_found, msg="authorization header was missing from the BQ request.")
    
    def _setup_mocks(self, api_url_mock):
        api_url_mock.__str__.return_value = self.API_BASE_URL

    def test_proxy_using_library(self):
        env = EnvironmentVarGuard()
        env.unset('KAGGLE_USER_SECRETS_TOKEN')
        with env:
            client = PublicBigqueryClient()
            self._test_proxy(client, should_use_proxy=True)

    def test_proxy_no_project(self):
        env = EnvironmentVarGuard()
        env.unset('KAGGLE_USER_SECRETS_TOKEN')
        with env:
            client = bigquery.Client()
            self._test_proxy(client, should_use_proxy=True)

    def test_proxy_with_kwargs(self):
        env = EnvironmentVarGuard()
        env.unset('KAGGLE_USER_SECRETS_TOKEN')
        with env:
            client = bigquery.Client(
                default_query_job_config=bigquery.QueryJobConfig(maximum_bytes_billed=int(1e9)))
            self._test_proxy(client, should_use_proxy=True)

    @patch.object(Connection, 'API_BASE_URL')
    @patch.object(kaggle_secrets.UserSecretsClient, 'get_bigquery_access_token', return_value=('secret',1000))
    def test_project_with_connected_account(self, mock_access_token, ApiUrlMock):
        self._setup_mocks(ApiUrlMock)
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        with env:
            client = bigquery.Client(
                project='ANOTHER_PROJECT', credentials=KaggleKernelCredentials())
            self._test_proxy(client, should_use_proxy=False)

    @patch.object(Connection, 'API_BASE_URL')
    @patch.object(kaggle_secrets.UserSecretsClient, 'get_bigquery_access_token', return_value=('secret',1000))
    def test_project_with_empty_integrations(self, mock_access_token, ApiUrlMock):
        self._setup_mocks(ApiUrlMock)
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', '')
        with env:
            client = bigquery.Client(
                project='ANOTHER_PROJECT', credentials=KaggleKernelCredentials())
            self._test_proxy(client, should_use_proxy=False)

    @patch.object(Connection, 'API_BASE_URL')
    @patch.object(kaggle_secrets.UserSecretsClient, 'get_bigquery_access_token', return_value=('secret',1000))
    def test_project_with_connected_account_unrelated_integrations(self, mock_access_token, ApiUrlMock):
        self._setup_mocks(ApiUrlMock)
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'GCS:ANOTHER_ONE')
        with env:
            client = bigquery.Client(
                project='ANOTHER_PROJECT', credentials=KaggleKernelCredentials())
            self._test_proxy(client, should_use_proxy=False)

    @patch.object(Connection, 'API_BASE_URL')
    @patch.object(kaggle_secrets.UserSecretsClient, 'get_bigquery_access_token', return_value=('secret',1000))
    def test_project_with_connected_account_default_credentials(self, mock_access_token, ApiUrlMock):
        self._setup_mocks(ApiUrlMock)
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'BIGQUERY')
        with env:
            client = bigquery.Client(project='ANOTHER_PROJECT')
            self._test_proxy(client, should_use_proxy=False)

    @patch.object(Connection, 'API_BASE_URL')
    @patch.object(kaggle_secrets.UserSecretsClient, 'get_bigquery_access_token', return_value=('secret',1000))
    def test_project_with_env_var_project_default_credentials(self, mock_access_token, ApiUrlMock):
        self._setup_mocks(ApiUrlMock)
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'BIGQUERY')
        env.set('GOOGLE_CLOUD_PROJECT', 'ANOTHER_PROJECT')
        with env:
            client = bigquery.Client()
            self._test_proxy(client, should_use_proxy=False)

    @patch.object(Connection, 'API_BASE_URL')
    @patch.object(kaggle_secrets.UserSecretsClient, 'get_bigquery_access_token', return_value=('secret',1000))
    def test_simultaneous_clients(self, mock_access_token, ApiUrlMock):
        self._setup_mocks(ApiUrlMock)
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        with env:
            proxy_client = bigquery.Client()
            self._test_proxy(proxy_client, should_use_proxy=True)
            bq_client = bigquery.Client(
                project='ANOTHER_PROJECT', credentials=KaggleKernelCredentials())
            self._test_proxy(bq_client, should_use_proxy=False)
            # Verify that proxy client is still going to proxy to ensure global Connection
            # isn't being modified.
            self._test_proxy(proxy_client, should_use_proxy=True)

    def test_no_project_with_connected_account(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'BIGQUERY')
        with env:
            with self.assertRaises(DefaultCredentialsError):
                # TODO(vimota): Handle this case, either default to Kaggle Proxy or use some default project
                # by the user or throw a custom exception.
                client = bigquery.Client()
                self._test_proxy(client, should_use_proxy=False)

    def test_magics_with_connected_account_default_credentials(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'BIGQUERY')
        with env:
            import sitecustomize
            sitecustomize.init()
            from google.cloud.bigquery import magics
            self.assertEqual(type(magics.context._credentials), KaggleKernelCredentials)
            magics.context.credentials = None

    def test_magics_without_connected_account(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        with env:
            import sitecustomize
            sitecustomize.init()
            from google.cloud.bigquery import magics
            self.assertIsNone(magics.context._credentials)
