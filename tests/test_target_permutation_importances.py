import unittest

import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
import target_permutation_importances as tpi


class TestTargetPermutationImportances(unittest.TestCase):
    def test_with_functional_api(self):
        data = load_breast_cancer()

        # Convert to a pandas dataframe
        Xpd = pd.DataFrame(data.data, columns=data.feature_names)

        # Compute permutation importances with default settings
        result_df = tpi.compute(
            model_cls=RandomForestClassifier,  # The constructor/class of the model.
            model_cls_params={},  # The parameters to pass to the model constructor. Update this based on your needs.
            model_fit_params={},  # The parameters to pass to the model fit method. Update this based on your needs.
            X=Xpd,  # pd.DataFrame, np.ndarray
            y=data.target,  # pd.Series, np.ndarray
            num_actual_runs=2,
            num_random_runs=3,
            # Options: {compute_permutation_importance_by_subtraction, compute_permutation_importance_by_division}
            # Or use your own function to calculate.
            permutation_importance_calculator=tpi.compute_permutation_importance_by_subtraction,
        )

        self.assertTrue(isinstance(result_df, pd.DataFrame))
        self.assertTrue("feature" in result_df.columns)
        self.assertTrue("importance" in result_df.columns)
        self.assertTrue(result_df.shape[0] == Xpd.shape[1])
        self.assertTrue(result_df["feature"].isna().sum() == 0)
        self.assertTrue(result_df["importance"].isna().sum() == 0)

    def test_with_sklearn_api(self):
        data = load_breast_cancer()

        # Convert to a pandas dataframe
        Xpd = pd.DataFrame(data.data, columns=data.feature_names)

        # Compute permutation importances with default settings
        wrapped_model = tpi.TargetPermutationImportancesWrapper(
            model_cls=RandomForestClassifier,  # The constructor/class of the model.
            model_cls_params={},  # The parameters to pass to the model constructor. Update this based on your needs.
            num_actual_runs=2,
            num_random_runs=10,
            # Options: {compute_permutation_importance_by_subtraction, compute_permutation_importance_by_division}
            # Or use your own function to calculate.
            permutation_importance_calculator=tpi.compute_permutation_importance_by_subtraction,
        )
        wrapped_model.fit(
            X=Xpd,  # pd.DataFrame, np.ndarray
            y=data.target,  # pd.Series, np.ndarray
            # And other fit parameters for the model.
        )
        # Get the feature importances as a pandas dataframe
        result_df = wrapped_model.feature_importances_df
        self.assertTrue(isinstance(result_df, pd.DataFrame))
        self.assertTrue("feature" in result_df.columns)
        self.assertTrue("importance" in result_df.columns)
        self.assertTrue(result_df.shape[0] == Xpd.shape[1])
        self.assertTrue(result_df["feature"].isna().sum() == 0)
        self.assertTrue(result_df["importance"].isna().sum() == 0)
