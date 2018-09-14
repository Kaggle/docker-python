import unittest

import shap

class TestShap(unittest.TestCase):
    def test_init(self):
        shap.initjs()
