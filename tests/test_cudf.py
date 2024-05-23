import unittest

from common import gpu_test, p100_exempt


class TestCudfDataFrame(unittest.TestCase):
    @gpu_test
    @p100_exempt
    def test_cudf_dataframe_operations(self):
        import cudf

        data = {'col1': [1, 2, 3], 'col2': [4, 5, 6]}
        gdf = cudf.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})

        gdf['col3'] = gdf['col1'] + gdf['col2']

        expected_col3 = cudf.Series([5, 7, 9])
        self.assertEqual(gdf.shape, (3, 2))
        self.assertEqual(list(gdf.columns), ['col1', 'col2'])
        self.assertTrue(gdf['col3'].equals(expected_col3)) 