import json
import unittest
import threading

from test.support.os_helper import EnvironmentVarGuard
from urllib.parse import urlparse

from http.server import BaseHTTPRequestHandler, HTTPServer

class HTTPHandler(BaseHTTPRequestHandler):
    called = False

    def do_HEAD(self):
        self.send_response(200)

    def do_GET(self):
        print('YO MOD', self.path)
        HTTPHandler.called = True
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

class TestGoogleGenerativeAiPatchDisabled(unittest.TestCase):
    http_endpoint = "http://127.0.0.1:80"
    grpc_endpoint = "http://127.0.0.1:50001"

    def test_disabled(self):
        env = EnvironmentVarGuard()
        env.set("KAGGLE_USER_SECRETS_TOKEN", "foobar")
        env.set("KAGGLE_DATA_PROXY_TOKEN", "foobar")
        env.set("KAGGLE_DATA_PROXY_URL", self.http_endpoint)
        env.set("KAGGLE_GRPC_DATA_PROXY_URL", self.grpc_endpoint)
        env.set("KAGGLE_DISABLE_GOOGLE_GENERATIVE_AI_INTEGRATION", "True")
        server_address = urlparse(self.http_endpoint)
        with env:
            with HTTPServer((server_address.hostname, server_address.port), HTTPHandler) as httpd:
                threading.Thread(target=httpd.serve_forever).start()
                import google.generativeai as palm
                palm.configure(api_key = "NotARealAPIKey")
                try:
                    for _ in palm.list_models():
                        pass
                except:
                    pass
                httpd.shutdown()
                self.assertFalse(HTTPHandler.called)
