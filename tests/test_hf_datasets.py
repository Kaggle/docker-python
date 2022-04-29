import unittest

from datasets import Dataset


class TestHuggingFaceDatasets(unittest.TestCase):

    def test_map(self):
        def some_func(batch):
            batch['label'] = 'foo'
            return batch
            
        df = Dataset.from_dict({'text': ['Kaggle rocks!']})
        mapped_df = df.map(some_func)
        
        self.assertEqual('foo', mapped_df[0]['label'])