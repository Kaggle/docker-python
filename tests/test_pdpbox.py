import numpy as np
import pandas as pd
from pdpbox import pdp
import unittest
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

class TestPdpbox(unittest.TestCase):
    def test_simple_pdp(self):
        # set up data
        data = pd.read_csv("/input/tests/data/fifa_2018_stats.csv")
        y = (data['Man of the Match'] == "Yes")
        feature_names = [i for i in data.columns if data[i].dtype in [np.int64]]
        X = data[feature_names]
        train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=1)
        # Build simple model
        tree_model = DecisionTreeClassifier(random_state=0,
                                            max_depth=3).fit(train_X, train_y)

        # Set up pdp as table
        pdp_goals = pdp.pdp_isolate(model=tree_model,
                                    dataset=val_X,
                                    model_features=feature_names,
                                    feature='Goal Scored')
        # make plot
        pdp.pdp_plot(pdp_goals, 'Goal Scored')
