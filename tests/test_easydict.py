import unittest

import easydict

class TestEasyDict(unittest.TestCase):
    def test_easydict(self):
        dict_src = {'foo': 3, 'bar': {'x': 1, 'y': 2}}
        d = easydict.EasyDict(dict_src)

        self.assertEqual(d.foo, dict_src['foo'])
        self.assertEqual(d.bar.x, dict_src['bar']['x'])
