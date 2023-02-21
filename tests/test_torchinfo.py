import unittest

import torch.nn as tnn

from torchinfo import summary

class TestTorchinfo(unittest.TestCase):
    def test_info(self):
        model = tnn.Linear(5,3)
        s = summary(model)
        self.assertIn('Layer', s)
