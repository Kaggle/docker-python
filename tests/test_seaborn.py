import unittest

import seaborn as sns

class TestSeaborn(unittest.TestCase):
    def test_option(self):
        sns.set(style="darkgrid")
