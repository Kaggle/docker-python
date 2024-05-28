import os
import threading
import re

from contextlib import contextmanager
from urllib.parse import urlparse
from test.support.os_helper import EnvironmentVarGuard
from http.server import BaseHTTPRequestHandler, HTTPServer

class KaggleAPIHandler(BaseHTTPRequestHandler):
    """
    Fake Kaggle API server supporting the download endpoint.
    Serving files under /input/tests/data/kagglehub.
    """
    def do_HEAD(self):
        self.send_response(200)

    def do_GET(self):
        m = re.match("^/api/v1/models/(.+)/download/(.+)$", self.path)
        if not m:
            self.send_response(404)
            self.wfile.write(bytes(f"Unhandled path: {self.path}", "utf-8"))
            return

        model_handle = m.group(1)
        path = m.group(2)
        filepath = f"/input/tests/data/kagglehub/models/{model_handle}/{path}"
        if not os.path.isfile(filepath):
            self.send_error(404, "Internet is disabled in our tests "
                "kagglehub uses a fake API server. "
                f"Use `kagglehub.model_download('{model_handle}', path='{path}')` to download the missing file "
                f"and copy it to `./docker-python/tests/data/kagglehub/models/{model_handle}/{path}`.")
            return

        with open(filepath, "rb") as f:
            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.send_header("Content-Length", os.path.getsize(filepath))
            self.end_headers()
            self.wfile.write(f.read())

@contextmanager
def create_test_kagglehub_server():
    endpoint = 'http://localhost:7777'
    env = EnvironmentVarGuard()
    env.set('KAGGLE_API_ENDPOINT', endpoint)
    test_server_address = urlparse(endpoint)
    with env:
        if not test_server_address.hostname or not test_server_address.port:
            msg = f"Invalid test server address: {endpoint}. You must specify a hostname & port"
            raise ValueError(msg)
        with HTTPServer((test_server_address.hostname, test_server_address.port), KaggleAPIHandler) as httpd:
            threading.Thread(target=httpd.serve_forever).start()

            try:
                yield httpd
            finally:
                httpd.shutdown()


