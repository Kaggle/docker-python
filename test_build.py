# This script should run without errors whenever we update the
# kaggle/python container. It checks that all our most popular packages can
# be loaded and used without errors.

import numpy as np
print("Numpy imported ok")
print("Your lucky number is: " + str(np.random.randint(100)))

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
plt.switch_backend('agg')
plt.plot(np.linspace(0,1,50), np.random.rand(50))
plt.savefig("plot1.png")
print("matplotlib.pyplot ok")

from mpl_toolkits.basemap import Basemap
print("Basemap ok")

import plotly.plotly as py
import plotly.graph_objs as go
print("plotly ok")

from ggplot import *
print("ggplot ok")

import theano
print("Theano ok")

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD
print("keras ok")

import nltk
from nltk.stem import WordNetLemmatizer
print("nltk ok")

import tensorflow as tf
hello = tf.constant('TensorFlow ok')
sess = tf.Session()
print(sess.run(hello))

import cv2
img = cv2.imread('plot1.png',0)
print("OpenCV ok")

from skimage.io import imread
print("skimage ok")

import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from google.cloud import bigquery

HOSTNAME = "127.0.0.1"
PORT = 8000
URL = "http://%s:%s" % (HOSTNAME, PORT)

header_found = False

class HTTPHandler(BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)

    def do_GET(s):
        global header_found
        header_found = any(k for k in s.headers if k == "X-KAGGLE-PROXY-DATA" and s.headers[k] == "test-key")
        s.send_response(200)

httpd = HTTPServer((HOSTNAME, PORT), HTTPHandler)
threading.Thread(target=httpd.serve_forever).start()

client = bigquery.Client()

try:
    for ds in client.list_datasets(): pass
except:
    pass

if header_found:
    print("bigquery proxy ok")
else:
    print("bigquery proxy failed")

httpd.shutdown()
