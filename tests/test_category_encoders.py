import unittest

## Need to make sure we have CountEncoder available from the category_encoders library
class TestCategoryEncoders(unittest.TestCase):
    def test_count_encoder(self):

        from category_encoders import CountEncoder
        import pandas as pd

        encoder = CountEncoder(cols="data")

        data = pd.DataFrame([1, 2, 3, 1, 4, 5, 3, 1], columns=["data"])

        encoded = encoder.fit_transform(data)
        self.assertTrue((encoded.data == [3, 1, 2, 3, 1, 1, 2, 3]).all())

