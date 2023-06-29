import unittest

import rapidfuzz

class TestRapidfuzz(unittest.TestCase):
    def test_distance(self):
        distance = rapidfuzz.distance.Levenshtein.distance(
            'Levenshtein', 'Lenvinsten'
        )

        self.assertEqual(4, distance)
