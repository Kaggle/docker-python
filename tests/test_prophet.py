import unittest

import numpy as np
import pandas as pd

from prophet import Prophet

class TestProphet(unittest.TestCase):
    def test_fit(self):
        train = pd.DataFrame({
            'ds': np.array(['2012-05-18', '2012-05-19', '2012-05-20', '2012-05-21', '2012-05-22']),
            'y': np.array([38.23, 21.25, 20.18, 20.01, 19.02])
        })

        forecaster = Prophet(mcmc_samples=1)
        forecaster.fit(train, adapt_engaged=False)

        self.assertEqual(len(train) + 1, len(forecaster.make_future_dataframe(periods=1)))
