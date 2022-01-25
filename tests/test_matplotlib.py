import unittest
import os.path

import matplotlib.pyplot as plt
import numpy as np

class TestMatplotlib(unittest.TestCase):
    def test_plot(self):
        plt.plot(np.linspace(0,1,50), np.random.rand(50))
        plt.savefig("plot1.png")

        self.assertTrue(os.path.isfile("plot1.png"))
