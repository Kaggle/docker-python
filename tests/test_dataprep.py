import unittest

import dataprep.eda as de
from dataprep.datasets import load_dataset


class TestDataPrep(unittest.TestCase):
    def test_report(self):
        df = load_dataset("titanic")
        de.create_report(df)
