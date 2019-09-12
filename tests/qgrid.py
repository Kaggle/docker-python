import unittest
import pandas as pd
from qgrid import QgridWidget

class TestQgrid(unittest.TestCase):
    def test_nans():
        df = pd.DataFrame([(pd.Timestamp('2017-02-02'), np.nan),
                           (4, 2),
                           ('foo', 'bar')])
        view = QgridWidget(df=df)
        view._handle_qgrid_msg_helper({
            'type': 'change_sort',
            'sort_field': 1,
            'sort_ascending': True
        })
