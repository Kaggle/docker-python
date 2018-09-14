import unittest

from fastai.core import partition

class TestFastAI(unittest.TestCase):
    def test_partition(self):
        result = partition([1,2,3,4,5], 2)

        self.assertEqual(3, len(result))
