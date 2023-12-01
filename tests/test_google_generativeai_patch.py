import unittest
import threading
from test.support.os_helper import EnvironmentVarGuard
from urllib.parse import urlparse

from http.server import BaseHTTPRequestHandler, HTTPServer

class HTTPHandler(BaseHTTPRequestHandler):
    called = False
    data_proxy_token_header_found = False
    user_secrets_token_header_found = False

    def do_HEAD(self):
        self.send_response(200)

    def do_GET(self):
        HTTPHandler.called = True
        HTTPHandler.data_proxy_token_header_found = any(
            k for k in self.headers if k == "x-kaggle-proxy-data")
        HTTPHandler.user_secrets_token_header_found = any(
            k for k in self.headers if k == "x-kaggle-authorization")
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

class TestGoogleGenerativeAiPatch(unittest.TestCase):    
    def test_headers_are_set(self):
        endpoint = "http://127.0.0.1:80"
        env = EnvironmentVarGuard()
        env.set('KAGGLE_USER_SECRETS_TOKEN', 'foobar')
        env.set('KAGGLE_DATA_PROXY_TOKEN', 'foobar')
        env.set('KAGGLE_DATA_PROXY_URL', endpoint)
        server_address = urlparse(endpoint)
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
                self.assertTrue(HTTPHandler.data_proxy_token_header_found)
                self.assertTrue(HTTPHandler.user_secrets_token_header_found)

