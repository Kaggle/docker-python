import unittest
import os.path
from xvfbwrapper import Xvfb

class TestXvfbwrapper(unittest.TestCase):
    def test_xvfb(self):
        vdisplay = Xvfb()
        vdisplay.start()
        display_var = ':{}'.format(vdisplay.new_display)
        self.assertEqual(display_var, os.environ['DISPLAY'])
        vdisplay.stop()
