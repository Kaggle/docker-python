import unittest

import Levenshtein

class TestLevenshtein(unittest.TestCase):
    def test_distance(self):
        distance = Levenshtein.distance('Levenshtein', 'Lenvinsten')

        self.assertEqual(4, distance)