import unittest

import polars as pl

class TestPolars(unittest.TestCase):
    def test_read_csv(self):
        data = pl.read_csv('/input/tests/data/train.csv')

        self.assertEqual(100, len(data))

    def test_plot(self):
        # This relies on the hvplot package
        data = pl.read_csv('/input/tests/data/train.csv')
        data.plot.line()

