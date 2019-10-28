import unittest

import numpy as np
import pandas as pd

from fbprophet import Prophet

class TestFbProphet(unittest.TestCase):
    def test_fit(self):
        train = pd.DataFrame({
            'ds': np.array(['2012-05-18', '2012-05-20']),
            'y': np.array([38.23, 21.25])
        })

        forecaster = Prophet(mcmc_samples=1)
        forecaster.fit(train, control={'adapt_engaged': False})
