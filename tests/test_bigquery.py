import unittest
import os
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer

from google.cloud import bigquery

HOSTNAME = "127.0.0.1"
PORT = 8000
URL = "http://%s:%s" % (HOSTNAME, PORT)

class TestBigQuery(unittest.TestCase):
    def _test_proxy(self, client):
        with HTTPServer((HOSTNAME, PORT), HTTPHandler) as httpd:
            threading.Thread(target=httpd.serve_forever).start()

            try:
                for ds in client.list_datasets(): pass
            except:
                pass

            httpd.shutdown()
            self.assertTrue(HTTPHandler.called, msg="Fake server did not receive a request from the BQ client.")
            self.assertTrue(HTTPHandler.header_found, msg="X-KAGGLE-PROXY-DATA header was missing from the BQ request.")
    
    def test_proxy_kaggle_project(self):
        client = bigquery.Client(project='KAGGLE')
        self._test_proxy(client)

    def test_proxy_no_project(self):
        client = bigquery.Client()
        self._test_proxy(client)

class HTTPHandler(BaseHTTPRequestHandler):
    called = False
    header_found = False

    def do_HEAD(s):
        s.send_response(200)

    def do_GET(s):
        HTTPHandler.called = True
        HTTPHandler.header_found = any(k for k in s.headers if k == "X-KAGGLE-PROXY-DATA" and s.headers[k] == "test-key")
        s.send_response(200)
