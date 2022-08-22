import unittest

import pandas as pd
from pandas.testing import assert_frame_equal


class TestPandasPytables(unittest.TestCase):

    def test_rw_hd5(self):
        want = pd.DataFrame([[1, 1.0, 'a']], columns=['x', 'y', 'z'])
        want.to_hdf('./want.h5', 'data')
        got = pd.read_hdf('./want.h5')
        assert_frame_equal(want, got)
