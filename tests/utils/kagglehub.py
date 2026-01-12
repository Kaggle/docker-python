import json
import os
import threading
import re

from contextlib import contextmanager
from urllib.parse import urlparse
from test.support.os_helper import EnvironmentVarGuard
from http.server import BaseHTTPRequestHandler, HTTPServer

from kagglesdk.kaggle_env import get_endpoint, get_env

class KaggleAPIHandler(BaseHTTPRequestHandler):
    """
    Fake Kaggle API server supporting the download endpoint.
    Serving files under /input/tests/data/kagglehub.
    """
    def do_HEAD(self):
        self.send_response(200)

    def do_POST(self):
        # 1. Get the content length from the headers
        content_length = int(self.headers.get('Content-Length', 0))
        
        # 2. Read the specified number of bytes from the input file (rfile)
        body_bytes = self.rfile.read(content_length)
        
        # 3. Decode the bytes to a string
        request_body = json.loads(body_bytes.decode('utf-8'))

        if self.path != "/api/v1/models.ModelApiService/DownloadModelInstanceVersion":
            self.send_response(404)
            self.wfile.write(bytes(f"Unhandled path: {self.path}", "utf-8"))
            return

        model_handle = f"{request_body["ownerSlug"]}/{request_body["modelSlug"]}/keras/{request_body["instanceSlug"]}/{request_body["versionNumber"]}"
        path = request_body["path"]
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
    env = EnvironmentVarGuard()
    env.set('KAGGLE_API_ENVIRONMENT', 'TEST')
    with env:
        endpoint = get_endpoint(get_env())
        test_server_address = urlparse(endpoint)

        with HTTPServer((test_server_address.hostname, test_server_address.port), KaggleAPIHandler) as httpd:
            threading.Thread(target=httpd.serve_forever).start()

            try:
                yield httpd
            finally:
                httpd.shutdown()


