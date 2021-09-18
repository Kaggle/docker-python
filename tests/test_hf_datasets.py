import unittest

from datasets import Dataset


class TestHfDatasets(unittest.TestCase):
    def test_adam_w(self):
        dset = Dataset.from_dict({"col1": ["a", "b", "c"], "col2": [1, 2, 3]})
        self.assertEqual(dset.num_rows, 3)
        self.assertEqual(dset.num_columns, 2)
