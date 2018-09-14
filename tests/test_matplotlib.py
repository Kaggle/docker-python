import unittest
import os.path

import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.basemap import Basemap

class TestMatplotlib(unittest.TestCase):
    def test_plot(self):
        plt.plot(np.linspace(0,1,50), np.random.rand(50))
        plt.savefig("plot1.png")

        self.assertTrue(os.path.isfile("plot1.png"))

    def test_basemap(self):
        Basemap(width=100,height=100,projection='aeqd',
                lat_0=40,lon_0=-105)
