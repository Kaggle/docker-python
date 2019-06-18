import unittest

import mock

from google.cloud import storage

def _make_credentials():
    import google.auth.credentials
    return mock.Mock(spec=google.auth.credentials.Credentials)

class TestStorage(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(storage.__version__)

    def test_ctr(self):
        credentials = _make_credentials()
        client = storage.Client(project="xyz", credentials=credentials)
        self.assertEqual(client.project, "xyz")

    def test_annonymous_client(self):
        anonymous = storage.Client.create_anonymous_client()
        self.assertIsNotNone(anonymous)
