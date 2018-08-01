# This script should run without errors whenever we update the
# kaggle/python container. It checks that all our most popular packages can
# be loaded and used without errors.

import tensorflow as tf
print(tf.__version__)
hello = tf.constant('TensorFlow ok')
sess = tf.Session()
print(sess.run(hello))
print("Tensorflow ok")

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD
print("Keras ok")

# Test Kaggle learntools
from learntools.core import binder; binder.bind(globals())
from learntools.python.ex1 import *
color="blue"
q0.check()
print("learntools ok")

# PyTorch smoke test based on http://pytorch.org/tutorials/beginner/nlp/deep_learning_tutorial.html
import torch
import torch.nn as tnn
import torch.autograd as autograd
torch.manual_seed(31337)
linear_torch = tnn.Linear(5,3)
data_torch = autograd.Variable(torch.randn(2, 5))
print(linear_torch(data_torch))
print("PyTorch ok")

import fastai
from fastai.io import get_data
print("fast.ai ok")

import numpy as np
print("Numpy imported ok")
print("Your lucky number is: " + str(np.random.randint(100)))

# Numpy must be linked to the MKL. (Occasionally, a third-party package will muck up the installation
# and numpy will be reinstalled with an OpenBLAS backing.)
from numpy.distutils.system_info import get_info
# This will throw an exception if the MKL is not linked correctly.
get_info("blas_mkl")

import pandas as pd
print("Pandas imported ok")

from sklearn import datasets
print("sklearn imported ok")
iris = datasets.load_iris()
X, y = iris.data, iris.target

from sklearn.ensemble import RandomForestClassifier
rf1 = RandomForestClassifier()
rf1.fit(X,y)
print("sklearn RandomForestClassifier: ok")

from sklearn.linear_model import LinearRegression
boston = datasets.load_boston()
X, y = boston.data, boston.target
lr1 = LinearRegression()
lr1.fit(X,y)
print("sklearn LinearRegression: ok")

from xgboost import XGBClassifier
xgb1 = XGBClassifier(n_estimators=3)
xgb1.fit(X[0:70],y[0:70])
print("xgboost XGBClassifier: ok")

import matplotlib.pyplot as plt
plt.plot(np.linspace(0,1,50), np.random.rand(50))
plt.savefig("plot1.png")
print("matplotlib.pyplot ok")

from mpl_toolkits.basemap import Basemap
print("Basemap ok")

import plotly.plotly as py
import plotly.graph_objs as go
print("plotly ok")

import theano
print("Theano ok")

import nltk
from nltk.stem import WordNetLemmatizer
print("nltk ok")

import cv2
img = cv2.imread('plot1.png',0)
print("OpenCV ok")

from skimage.io import imread
print("skimage ok")

from wordbatch.extractors import WordBag
print("wordbatch ok")

import pyfasttext
print("pyfasttext ok")

import fastText
print("fastText ok")

import mxnet
import mxnet.gluon
print("mxnet ok")

import bokeh
print("bokeh ok")

import seaborn
print("seaborn ok")

# Test BigQuery
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from google.cloud import bigquery
HOSTNAME = "127.0.0.1"
PORT = 8000
URL = "http://%s:%s" % (HOSTNAME, PORT)
fake_bq_called = False
fake_bq_header_found = False
class HTTPHandler(BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)

    def do_GET(s):
        global fake_bq_called
        global fake_bq_header_found
        fake_bq_called = True
        fake_bq_header_found = any(k for k in s.headers if k == "X-KAGGLE-PROXY-DATA" and s.headers[k] == "test-key")
        s.send_response(200)

httpd = HTTPServer((HOSTNAME, PORT), HTTPHandler)
threading.Thread(target=httpd.serve_forever).start()
client = bigquery.Client()
try:
    for ds in client.list_datasets(): pass
except:
    pass
httpd.shutdown()
assert fake_bq_called, "Fake server did not recieve a request from the BQ client."
assert fake_bq_header_found, "X-KAGGLE-PROXY-DATA header was missing from the BQ request."
print("bigquery proxy ok")

import shap
print("shap ok")

import kmapper
print("kmapper ok")

from vowpalwabbit import pyvw
vw = pyvw.vw(quiet=True)
ex = vw.example('1 | a b c')
vw.learn(ex)
print(vw.predict(ex))
print('vowpalwabbit ok')

import essentia
print(essentia.__version__)
print("Essentia ok")
