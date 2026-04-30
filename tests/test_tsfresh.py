import unittest

import pandas as pd
import numpy as np

try:
    from tsfresh import extract_features
    HAS_TSFRESH = True
except ImportError:
    HAS_TSFRESH = False

@unittest.skipUnless(HAS_TSFRESH, 'tsfresh is not importable (may require CUDA libs)')
class TestTsFresh(unittest.TestCase):
    def test_extract_feature(self):
        ts = pd.DataFrame({
            'id': np.array(['a', 'a', 'a', 'b', 'b', 'b']),
            'time': np.array([0,1,2,0,1,2]),
            'x': np.array([3,4,5,7,8,10])
        })
        extracted_features = extract_features(ts, column_id='id', column_sort='time', n_jobs=1)
        self.assertEqual(2, len(extracted_features))
