import json
import unittest
import threading

from test.support.os_helper import EnvironmentVarGuard
from urllib.parse import urlparse

from http.server import BaseHTTPRequestHandler, HTTPServer

class HTTPHandler(BaseHTTPRequestHandler):
    called = False
    path = None
    headers = {}

    def do_HEAD(self):
        self.send_response(200)

    def do_GET(self):
        HTTPHandler.path = self.path
        HTTPHandler.headers = self.headers
        HTTPHandler.called = True
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

class TestGoogleGenerativeAiPatch(unittest.TestCase):
    endpoint = "http://127.0.0.1:80"

    def test_proxy_enabled(self):
        env = EnvironmentVarGuard()
        secrets_token = "secrets_token"
        proxy_token = "proxy_token"
        env.set("KAGGLE_USER_SECRETS_TOKEN", secrets_token)
        env.set("KAGGLE_DATA_PROXY_TOKEN", proxy_token)
        env.set("KAGGLE_DATA_PROXY_URL", self.endpoint)
        env.set("KAGGLE_GRPC_DATA_PROXY_URL", "http://127.0.0.1:50001")
        env.set("KAGGLE_GOOGLE_GENERATIVE_AI_USE_REST_ONLY", "True")
        server_address = urlparse(self.endpoint)
        with env:
            with HTTPServer((server_address.hostname, server_address.port), HTTPHandler) as httpd:
                threading.Thread(target=httpd.serve_forever).start()
                import google.generativeai as palm
                api_key = "NotARealAPIKey"
                palm.configure(api_key = api_key)
                try:
                    for _ in palm.list_models():
                        pass
                except:
                    pass
                httpd.shutdown()
                self.assertTrue(HTTPHandler.called)
                self.assertIn("/palmapi", HTTPHandler.path)
                self.assertEqual(proxy_token, HTTPHandler.headers["x-kaggle-proxy-data"])
                self.assertEqual("Bearer {}".format(secrets_token), HTTPHandler.headers["x-kaggle-authorization"])
                self.assertEqual(api_key, HTTPHandler.headers["x-goog-api-key"])
