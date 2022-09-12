import unittest

import pandas as pd
from pandas.testing import assert_frame_equal


class TestPandasOpenPyXL(unittest.TestCase):

    def test_rw_excel(self):
        want = pd.DataFrame([[1, 10, 'a']], columns=['x', 'y', 'z'])
        want.to_excel('./want.xlsx', index=False, engine="openpyxl")
        got = pd.read_excel('./want.xlsx', engine="openpyxl")
        assert_frame_equal(want, got)