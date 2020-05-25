import unittest
import os.path

from ggplot import *

class TestGgplot(unittest.TestCase):

    def test_plot(self):
        p = ggplot(aes(x='mpg'), data=mtcars) + geom_histogram()
        p.save("myplot.png")

        self.assertTrue(os.path.isfile("myplot.png"))
