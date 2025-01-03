import unittest

import numpy as np
import pandas as pd
import tensorflow_decision_forests as tfdf

class TestTensorflowDecisionForest(unittest.TestCase):
    def test_fit(self):
        train_df = pd.read_csv("/input/tests/data/train.csv")

        # Convert the dataset into a TensorFlow dataset.
        train_ds = tfdf.keras.pd_dataframe_to_tf_dataset(train_df, label="label")
        
        # Train the model
        model = tfdf.keras.RandomForestModel(num_trees=1)
        model.fit(train_ds)

        self.assertEqual(1, model.count_params())