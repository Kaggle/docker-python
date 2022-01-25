import unittest

from flask import Flask, request

class TestFlask(unittest.TestCase):
    def test_request(self):
        app = Flask(__name__)
        with app.test_request_context('/foo', method='POST'):
            assert request.path == '/foo'
            assert request.method == 'POST'
