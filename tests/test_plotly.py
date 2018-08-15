import unittest

import plotly.graph_objs as go

class TestPlotly(unittest.TestCase):
    def test_figure(self):
        trace = {'x': [1, 2], 'y': [1, 3]}
        data = [ trace ]
        go.Figure(data=data)
