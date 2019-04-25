import unittest

from sklearn import datasets
from cuml import LinearRegression as cuLinearRegression
import cudf as gd

# For full unit tests of rapids cuml, please run the following commands after building the docker.
# docker run --runtime nvidia --rm -it kaggle/python-gpu-build /bin/bash
# export LD_LIBRARY_PATH=/usr/local/cuda/lib64
# conda uninstall --yes pytest && pip install -U pytest
# cd /opt/conda/lib/python3.6/site-packages/cuml/test
# pytest -v

class TestCuml(unittest.TestCase):

    def test_linearn_classifier(self):
        boston = datasets.load_boston()
        X, y = boston.data, boston.target
        df = pd.DataFrame(X,columns=['fea%d'%i for i in range(X.shape[1])])
        gdf = gd.from_pandas(df)
        lr = cuLinearRegression(fit_intercept=True,
                               normalize=False,
                               algorithm='svd')
        lr.fit(gdf,y)
