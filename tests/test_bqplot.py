import unittest
import numpy as np
import bqplot.pyplot as plt

class TestBqplot(unittest.TestCase):
    def test_figure(self):
        size = 100
        scale = 100.0
        np.random.seed(0)
        x_data = np.arange(size)
        y_data = np.cumsum(np.random.randn(size)  * scale)
        fig = plt.figure(title='First Example')
        plt.plot(y_data)
        fig.save_png()
