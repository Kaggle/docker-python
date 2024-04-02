import unittest

import datasets
import pandas as pd

class TestHuggingFaceDatasets(unittest.TestCase):

    def test_map(self):
        def some_func(batch):
            batch['label'] = 'foo'
            return batch
            
        df = datasets.Dataset.from_dict({'text': ['Kaggle rocks!']})
        mapped_df = df.map(some_func)
        
        self.assertEqual('foo', mapped_df[0]['label'])
        
    def test_load_dataset(self):
        dataset = datasets.load_dataset("csv", data_files="/input/tests/data/train.csv")
        full_data = pd.DataFrame(dataset['train'])
        self.assertFalse(full_data.empty)