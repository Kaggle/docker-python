import unittest
import pymagnitude

from pymagnitude import *

class TestPyMagnitude(unittest.TestCase):
    def test_has_vectors(self):
        vectors = Magnitude('/input/tests/data/vectors.magnitude')
        self.assertEqual(len(vectors), 2)

    def test_vector_search(self):
        vectors = Magnitude('/input/tests/data/vectors.magnitude')
        self.assertTrue('the' in vectors)

    def test_vector_query(self):
        vectors = Magnitude('/input/tests/data/vectors.magnitude')
        self.assertTrue(vectors.dim == len(vectors.query('the')))
