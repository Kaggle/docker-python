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