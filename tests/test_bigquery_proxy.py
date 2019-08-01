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
from kaggle_gcp import KaggleKernelCredentials, PublicBigqueryClient, init_bigquery
import kaggle_secrets


class TestBigQuery(unittest.TestCase):

    def _test_proxy(self, client):
        class HTTPHandler(BaseHTTPRequestHandler):
            called = False
            proxy_header_found = False

            def do_HEAD(self):
                self.send_response(200)

            def do_GET(self):
                HTTPHandler.called = True
                HTTPHandler.proxy_header_found = any(
                    k for k in self.headers if k == "X-KAGGLE-PROXY-DATA" and self.headers[k] == "test-key")
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

        server_address = urlparse(os.getenv('KAGGLE_DATA_PROXY_URL'))
        with HTTPServer((server_address.hostname, server_address.port), HTTPHandler) as httpd:
            threading.Thread(target=httpd.serve_forever).start()

            for dataset in client.list_datasets():
                self.assertEqual(dataset.dataset_id, "datasetname")    
            
            httpd.shutdown()
            self.assertTrue(
                    HTTPHandler.called, msg="Fake server was not called from the BQ client, but should have been.")
            self.assertTrue(
                HTTPHandler.proxy_header_found, msg="X-KAGGLE-PROXY-DATA header was missing from the BQ proxy request.")

    def test_proxy_using_library(self):
        env = EnvironmentVarGuard()
        env.unset('KAGGLE_USER_SECRETS_TOKEN')
        with env:
            client = PublicBigqueryClient()
            self._test_proxy(client)

    def test_proxy_no_project(self):
        env = EnvironmentVarGuard()
        env.unset('KAGGLE_USER_SECRETS_TOKEN')
        with env:
            client = bigquery.Client()
            self._test_proxy(client)
    
    def test_monkeypatching_idempotent(self):
        env = EnvironmentVarGuard()
        env.unset('KAGGLE_USER_SECRETS_TOKEN')
        with env:
            client1 = bigquery.Client
            init_bigquery()
            client2 = bigquery.Client
            self.assertEqual(client1, client2)

    def test_proxy_with_kwargs(self):
        env = EnvironmentVarGuard()
        env.unset('KAGGLE_USER_SECRETS_TOKEN')
        with env:
            client = bigquery.Client(
                default_query_job_config=bigquery.QueryJobConfig(maximum_bytes_billed=int(1e9)))
            self._test_proxy(client)
