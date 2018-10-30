import unittest

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

class TestCartopy(unittest.TestCase):
    def test_stem(self):
        factory = StemmerFactory()
				stemmer = factory.create_stemmer()