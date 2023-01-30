import unittest

import timm


class TestTimm(unittest.TestCase):
    def test_list_models(self):
        models = timm.list_models()
        self.assertGreater(len(models), 0)
