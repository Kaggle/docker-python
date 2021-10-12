import unittest

import vaex

class TestVaex(unittest.TestCase):
    def test_read_csv(self):
        df = vaex.read_csv("/input/tests/data/train.csv")

        self.assertEqual((100, 785), df.shape)
        self.assertEqual(10, df['label'].nunique())