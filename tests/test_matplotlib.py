import unittest
import os.path

from distutils.version import StrictVersion

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

class TestMatplotlib(unittest.TestCase):
    def test_version(self):
        # b/308525631: newer versions of Matplotlib causes learntools to fail
        self.assertLess(StrictVersion(matplotlib.__version__), StrictVersion("3.8.0"))

    def test_plot(self):
        plt.plot(np.linspace(0,1,50), np.random.rand(50))
        plt.savefig("plot1.png")

        self.assertTrue(os.path.isfile("plot1.png"))
