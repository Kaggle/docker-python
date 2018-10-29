import unittest
import os.path
from dipy.viz import window
from xvfbwrapper import Xvfb

class TestDipy(unittest.TestCase):
    out_file = 'test.png'
    def test_renderer(self):
        vdisplay = Xvfb()
        vdisplay.start()

        ren = window.Renderer()
        window.record(ren, n_frames=1, out_path=self.out_file, size=(600, 600))
        self.assertTrue(os.path.exists(self.out_file))

        vdisplay.stop()

    def tearDown(self):
        os.remove(self.out_file)
