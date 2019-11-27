import unittest

import numpy as np
import pandas as pd

from qgrid import QgridWidget


class TestQgrid(unittest.TestCase):
    def test_nans(self):
        df = pd.DataFrame([(pd.Timestamp('2017-02-02'), np.nan),
                           (4, 2),
                           ('foo', 'bar')])
        view = QgridWidget(df=df)
        
        self.assertIsNotNone(view.get_changed_df())
