import unittest

# needed for the Word Error Rate metric:
# competitions/metrics/python/deployed_metrics/general_use_metrics/word_error_rate.py
import rapidfuzz

class TestRapidfuzz(unittest.TestCase):
    def test_distance(self):
        distance = rapidfuzz.distance.Levenshtein.distance(
            'Levenshtein', 'Lenvinsten'
        )

        self.assertEqual(4, distance)
