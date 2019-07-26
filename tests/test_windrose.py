import unittest

import windrose

class TestWindrose(unittest.TestCase):
    def test_rotate(self):
        self.assertTrue(callable(windrose.plot_windrose))
