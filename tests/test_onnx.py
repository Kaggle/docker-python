import unittest

import onnx

class TestOnnx(unittest.TestCase):
    def test_load(self):
        model = onnx.load("data/mnist-8.onnx")
        self.assertIn("CNTKGraph", onnx.helper.printable_graph(model.graph))
