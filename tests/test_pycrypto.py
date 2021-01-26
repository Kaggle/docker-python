import unittest

from Crypto.Hash import SHA256

class TestPycrypto(unittest.TestCase):
    def test_digest(self):
        hash = SHA256.new()
        hash.update('message'.encode('utf-8'))
        h = hash.digest()
        self.assertEqual(h, b'\xabS\n\x13\xe4Y\x14\x98+y\xf9\xb7\xe3\xfb\xa9\x94\xcf\xd1\xf3\xfb"\xf7\x1c\xea\x1a\xfb\xf0+F\x0cm\x1d')
