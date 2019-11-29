import unittest

from annoy import AnnoyIndex


class TestAnnoy(unittest.TestCase):
    def test_tree(self):
        t = AnnoyIndex(5, 'angular')
        t.add_item(1, [1,2,3,4,5])

        self.assertTrue(t.build(1))
