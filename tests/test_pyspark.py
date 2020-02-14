import unittest

import math
import random

import pyspark

ss = pyspark.sql.SparkSession.builder\
    .appName('pyspark_pi_calculator')\
    .getOrCreate()


# Obtain Spark Context object
sc = ss.sparkContext


# Reference:
# 'Pi Estimation' example adopted from: https://spark.apache.org/examples.html

def inside(p):
    '''
    Tells whether a random point is inside a unit circle.
    '''
    x, y = random.random(), random.random()
    return x*x + y*y < 1


class TestPyspark(unittest.TestCase):
    def test_calculate_pi(self):
        global sc

        num_samples = 100000000
        count = sc.parallelize(range(0, num_samples)).filter(inside).count()
        pyspark_pi = 4.0 * count / num_samples

        self.assertAlmostEqual(pyspark_pi, math.pi, places=2)

