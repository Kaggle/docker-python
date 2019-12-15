import unittest

import wandb

class TestWandB(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(wandb.__version__)
