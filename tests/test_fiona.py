import unittest

import fiona
import pandas as pd

class TestFiona(unittest.TestCase):
    def test_read(self):
        with fiona.open("/input/tests/data/coutwildrnp.shp") as source:
            self.assertEqual(67, len(source))

