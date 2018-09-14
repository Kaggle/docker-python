import unittest

from bokeh.plotting import figure

class TestBokeh(unittest.TestCase):
    def test_figure(self):
        figure(title="Hello World")
