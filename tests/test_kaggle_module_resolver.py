import unittest

import os
import threading

import tensorflow as tf
import tensorflow_hub as hub

from http.server import BaseHTTPRequestHandler, HTTPServer
from test.support import EnvironmentVarGuard


class TestKaggleModuleResolver(unittest.TestCase):
    class HubHTTPHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'application/gzip')
            self.end_headers()

            with open('/input/tests/data/model.tar.gz', 'rb') as model_archive:
                self.wfile.write(model_archive.read())

    def _test_client(self, client_func, handler):
        with HTTPServer(('localhost', 8080), handler) as test_server:
            threading.Thread(target=test_server.serve_forever).start()

            try:
                client_func()            
            finally:
                test_server.shutdown()

    def test_kaggle_resolver_succeeds(self):
        # Simulates we are inside a Kaggle environment.
        env = EnvironmentVarGuard()
        env.set('KAGGLE_CONTAINER_NAME', 'foo')
        # Attach model to right directory.
        os.makedirs('/kaggle/input/foomodule/tensorflow2/barvar')
        os.symlink('/input/tests/data/saved_model/', '/kaggle/input/foomodule/tensorflow2/barvar/2', target_is_directory=True)

        with env:
            test_inputs = tf.ones([1,4])
            layer = hub.KerasLayer("https://kaggle.com/models/foo/foomodule/frameworks/TensorFlow2/variations/barvar/versions/2")
            self.assertEqual([1, 1], layer(test_inputs).shape)

    def test_kaggle_resolver_not_attached_throws(self):
        # Simulates we are inside a Kaggle environment.
        env = EnvironmentVarGuard()
        env.set('KAGGLE_CONTAINER_NAME', 'foo')
        with env:
            with self.assertRaisesRegex(RuntimeError, '.*attach.*'):
                hub.KerasLayer("https://kaggle.com/models/foo/foomodule/frameworks/TensorFlow2/variations/barvar/versions/2")

    def test_http_resolver_succeeds(self):
        def call_hub():
            test_inputs = tf.ones([1,4])
            layer = hub.KerasLayer('http://localhost:8080/model.tar.gz')
            self.assertEqual([1, 1], layer(test_inputs).shape)

        self._test_client(call_hub, TestKaggleModuleResolver.HubHTTPHandler)

    def test_local_path_resolver_succeeds(self):
        test_inputs = tf.ones([1,4])
        layer = hub.KerasLayer('/input/tests/data/saved_model')
        
        self.assertEqual([1, 1], layer(test_inputs).shape)
