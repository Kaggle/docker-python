import unittest

from pytext.config.field_config import FeatureConfig
from pytext.data.featurizer import InputRecord, SimpleFeaturizer

class TestPyText(unittest.TestCase):

    def test_tokenize(self):
        featurizer = SimpleFeaturizer.from_config(
            SimpleFeaturizer.Config(), FeatureConfig()
        )

        tokens = featurizer.featurize(InputRecord(raw_text="At eight o'clock")).tokens
        self.assertEqual(['at', 'eight', "o'clock"], tokens)
