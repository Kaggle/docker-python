import unittest
import os
import threading
from test.support import EnvironmentVarGuard
from urllib.parse import urlparse

from http.server import BaseHTTPRequestHandler, HTTPServer

from google.cloud import bigquery
from google.auth.exceptions import DefaultCredentialsError
from kaggle_gcp import KaggleKernelCredentials, PublicBigqueryClient


class TestBigQuery(unittest.TestCase):

    def _test_proxy(self, client, should_use_proxy):
        class HTTPHandler(BaseHTTPRequestHandler):
            called = False
            header_found = False

            def do_HEAD(self):
                self.send_response(200)

            def do_GET(self):
                HTTPHandler.called = True
                print(f"headers: {self.headers}")
                HTTPHandler.header_found = any(
                    k for k in self.headers if k == "X-KAGGLE-PROXY-DATA" and self.headers[k] == "test-key")
                self.send_response(200)

        server_address = urlparse(os.getenv('KAGGLE_DATA_PROXY_URL'))
        with HTTPServer((server_address.hostname, server_address.port), HTTPHandler) as httpd:
            threading.Thread(target=httpd.serve_forever).start()

            try:
                for _ in client.list_datasets():
                    pass
            except:
                pass

            httpd.shutdown()
            if should_use_proxy:
                self.assertTrue(
                    HTTPHandler.called, msg="Fake server did not receive a request from the BQ client.")
                self.assertTrue(
                    HTTPHandler.header_found, msg="X-KAGGLE-PROXY-DATA header was missing from the BQ request.")
            else:
                self.assertFalse(
                    HTTPHandler.called, msg="Fake server was called from the BQ client, but should not have been.")

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
                default_query_job_config=bigquery.QueryJobConfig(maximum_bytes_billed=1e9))
            self._test_proxy(client, should_use_proxy=True)

    def test_project_with_connected_account(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        with env:
            client = bigquery.Client(
                project='ANOTHER_PROJECT', credentials=KaggleKernelCredentials())
            self._test_proxy(client, should_use_proxy=False)

    def test_project_with_empty_integrations(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', '')
        with env:
            client = bigquery.Client(
                project='ANOTHER_PROJECT', credentials=KaggleKernelCredentials())
            self._test_proxy(client, should_use_proxy=False)

    def test_project_with_connected_account_unrelated_integrations(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'GCS:ANOTHER_ONE')
        with env:
            client = bigquery.Client(
                project='ANOTHER_PROJECT', credentials=KaggleKernelCredentials())
            self._test_proxy(client, should_use_proxy=False)

    def test_project_with_connected_account_default_credentials(self):
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_KERNEL_INTEGRATIONS', 'BIGQUERY')
        with env:
            client = bigquery.Client(project='ANOTHER_PROJECT')
            self._test_proxy(client, should_use_proxy=False)

    def test_simultaneous_clients(self):
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
