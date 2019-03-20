import unittest

from distutils.version import StrictVersion

import seaborn as sns

class TestSeaborn(unittest.TestCase):
    # Fails if seaborn gets downgraded by other package installations.
    def test_version(self):
        self.assertGreaterEqual(StrictVersion(sns.__version__), StrictVersion("0.9.0"))


    def test_option(self):
        sns.set(style="darkgrid")
