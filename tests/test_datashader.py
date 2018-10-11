import unittest

import numpy as np
import pandas as pd
import datashader as ds
import datashader.transfer_functions as tf

class TestDatashader(unittest.TestCase):
    # based on https://github.com/pyviz/datashader/blob/master/datashader/tests/test_pipeline.py
    def test_pipeline(self):
        df = pd.DataFrame({
            'x': np.array(([0.] * 10 + [1] * 10)),
            'y': np.array(([0.] * 5 + [1] * 5 + [0] * 5 + [1] * 5)),
            'f64': np.arange(20, dtype='f8')
        })
        df.f64.iloc[2] = np.nan

        cvs = ds.Canvas(plot_width=2, plot_height=2, x_range=(0, 1), y_range=(0, 1))

        pipeline = ds.Pipeline(df, ds.Point('x', 'y'))
        img = pipeline((0, 1), (0, 1), 2, 2)
        agg = cvs.points(df, 'x', 'y', ds.count())
        self.assertTrue(img.equals(tf.shade(agg)))

        color_fn = lambda agg: tf.shade(agg, 'pink', 'red')
        pipeline.color_fn = color_fn
        img = pipeline((0, 1), (0, 1), 2, 2)
        self.assertTrue(img.equals(color_fn(agg)))

        transform_fn = lambda agg: agg + 1
        pipeline.transform_fn = transform_fn
        img = pipeline((0, 1), (0, 1), 2, 2)
        self.assertTrue(img.equals(color_fn(transform_fn(agg))))

        pipeline = ds.Pipeline(df, ds.Point('x', 'y'), ds.sum('f64'))
        img = pipeline((0, 1), (0, 1), 2, 2)
        agg = cvs.points(df, 'x', 'y', ds.sum('f64'))
        self.assertTrue(img.equals(tf.shade(agg)))
