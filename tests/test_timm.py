import unittest

import timm


class TestTimm(unittest.TestCase):
    def assertList(self):
        models = timm.list_models()
        self.assertGreater(len(models), 0)
