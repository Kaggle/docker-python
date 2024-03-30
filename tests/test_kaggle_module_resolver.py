import unittest

import os
import threading
import json

import tensorflow as tf
import tensorflow_hub as hub

from http.server import BaseHTTPRequestHandler, HTTPServer
from test.support.os_helper import EnvironmentVarGuard
from contextlib import contextmanager
from kagglehub.exceptions import BackendError

MOUNT_PATH = "/kaggle/input"

@contextmanager
def create_test_server(handler_class):
    hostname = 'localhost'
    port = 8080
    addr = f"http://{hostname}:{port}"

    # Simulates we are inside a Kaggle environment.
    env = EnvironmentVarGuard()
    env.set('KAGGLE_KERNEL_RUN_TYPE', 'Interactive')
    env.set('KAGGLE_USER_SECRETS_TOKEN', 'foo jwt token')
    env.set('KAGGLE_DATA_PROXY_TOKEN', 'foo proxy token')
    env.set('KAGGLE_DATA_PROXY_URL', addr)

    with env:
        with HTTPServer((hostname, port), handler_class) as test_server:
            threading.Thread(target=test_server.serve_forever).start()

            try:
                yield addr
            finally:
                test_server.shutdown()

class HubHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/gzip')
        self.end_headers()

        with open('/input/tests/data/model.tar.gz', 'rb') as model_archive:
            self.wfile.write(model_archive.read())

class KaggleJwtHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.endswith("AttachDatasourceUsingJwtRequest"):
            content_length = int(self.headers["Content-Length"])
            request = json.loads(self.rfile.read(content_length))
            model_ref = request["modelRef"]

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            if model_ref['ModelSlug'] == 'unknown':
                self.wfile.write(bytes(json.dumps({
                    "wasSuccessful": False,
                }), "utf-8"))
                return

            # Load the files
            mount_slug = f"{model_ref['ModelSlug']}/{model_ref['Framework']}/{model_ref['InstanceSlug']}/{model_ref['VersionNumber']}"
            os.makedirs(os.path.dirname(os.path.join(MOUNT_PATH, mount_slug)))
            os.symlink('/input/tests/data/saved_model/', os.path.join(MOUNT_PATH, mount_slug), target_is_directory=True)

            # Return the response
            self.wfile.write(bytes(json.dumps({
                "wasSuccessful": True,
                "result": {
                    "mountSlug": mount_slug,
                },
            }), "utf-8"))
        else:
            self.send_response(404)
            self.wfile.write(bytes(f"Unhandled path: {self.path}", "utf-8"))

class TestKaggleModuleResolver(unittest.TestCase):
    def test_kaggle_resolver_long_url_succeeds(self):
        model_url = "https://kaggle.com/models/foo/foomodule/frameworks/TensorFlow2/variations/barvar/versions/2"
        with create_test_server(KaggleJwtHandler) as addr:
            test_inputs = tf.ones([1,4])
            layer = hub.KerasLayer(model_url)
            self.assertEqual([1, 1], layer(test_inputs).shape)
        # Delete the files that were created in KaggleJwtHandler's do_POST method
        os.unlink(os.path.join(MOUNT_PATH, "foomodule/tensorflow2/barvar/2"))
        os.rmdir(os.path.dirname(os.path.join(MOUNT_PATH, "foomodule/tensorflow2/barvar/2")))

    def test_kaggle_resolver_short_url_succeeds(self):
        model_url = "https://kaggle.com/models/foo/foomodule/TensorFlow2/barvar/2"
        with create_test_server(KaggleJwtHandler) as addr:
            test_inputs = tf.ones([1,4])
            layer = hub.KerasLayer(model_url)
            self.assertEqual([1, 1], layer(test_inputs).shape)
        # Delete the files that were created in KaggleJwtHandler's do_POST method
        os.unlink(os.path.join(MOUNT_PATH, "foomodule/tensorflow2/barvar/2"))
        os.rmdir(os.path.dirname(os.path.join(MOUNT_PATH, "foomodule/tensorflow2/barvar/2")))

    def test_kaggle_resolver_not_attached_throws(self):
        with create_test_server(KaggleJwtHandler) as addr:
            with self.assertRaises(BackendError):
                hub.KerasLayer("https://kaggle.com/models/foo/unknown/frameworks/TensorFlow2/variations/barvar/versions/2")

    def test_http_resolver_succeeds(self):
        with create_test_server(HubHTTPHandler) as addr:
            test_inputs = tf.ones([1,4])
            layer = hub.KerasLayer(f'{addr}/model.tar.gz')
            self.assertEqual([1, 1], layer(test_inputs).shape)

    def test_local_path_resolver_succeeds(self):
        test_inputs = tf.ones([1,4])
        layer = hub.KerasLayer('/input/tests/data/saved_model')
        
        self.assertEqual([1, 1], layer(test_inputs).shape)
