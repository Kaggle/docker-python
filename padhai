import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import mean_squared_error
from tqdm import tqdm_notebook
import operator
import json
np.random.seed(0)

class MPNeuron:
    
    def __init__(self):
        self.theta = None
        
    def mp_neuron(self, x):
        if sum(x) >= self.theta:
            return 1
        return 0
    
    def fit_brute_force(self, X, Y):
        accuracy = {}
        for theta in tqdm_notebook(range(0, X.shape[1]+1), total=X.shape[1]+1):
            self.theta = theta
            Y_pred = self.predict(X)
            accuracy[theta] = accuracy_score(Y, Y_pred)  
            
        sorted_accuracy = sorted(accuracy.items(), key=operator.itemgetter(1), reverse=True)
        best_theta, best_accuracy = sorted_accuracy[0]
        self.theta = best_theta
        
    def fit(self, X, Y, epochs=10, log=False, display_plot=False):
        self.theta = (X.shape[1]+1)//2
        if log or display_plot:
            accuracy = {}
        for i in tqdm_notebook(range(epochs), total=epochs, unit="epoch"):
            Y_pred = self.predict(X)
            tn, fp, fn, tp = confusion_matrix(Y, Y_pred).ravel()
            if fp > fn and self.theta <= X.shape[1]:
                self.theta += 1
            elif fp < fn and self.theta >= 1:
                self.theta -= 1
            else:
                continue
                
            if log or display_plot:
                Y_pred = self.predict(X)
                accuracy[i] = accuracy_score(Y, Y_pred)
        if log:
            with open('mp_neuron_accuracy.json', 'w') as fp:
                json.dump(accuracy, fp)
        if display_plot:
            epochs_, accuracy_ = zip(*accuracy.items())
            plt.plot(epochs_, accuracy_)
            plt.xlabel("Epochs")
            plt.ylabel("Train Accuracy")
            plt.show()
    
    def predict(self, X):
        Y = []
        for x in X:
            result = self.mp_neuron(x)
            Y.append(result)
        return np.array(Y)


class Perceptron:
    
    def __init__(self):
        self.w = None
        self.b = None
        
    def perceptron(self, x):
        return np.sum(self.w * x) + self.b
    
    def fit(self, X, Y, epochs=10, learning_rate=0.01, log=False, display_plot=False):
        # initialise the weights and bias
        self.w = np.random.randn(1, X.shape[1])
        self.b = 0
        if log or display_plot: 
            accuracy = {}
        for i in tqdm_notebook(range(epochs), total=epochs, unit="epoch"):
            for x, y in zip(X, Y):
                result = self.perceptron(x)
                if y == 1 and result < 0:
                    self.w += learning_rate*x
                    self.b += learning_rate
                elif y == 0 and result >= 0:
                    self.w -= learning_rate*x
                    self.b -= learning_rate
            if log or display_plot:
                Y_pred = self.predict(X)
                accuracy[i] = accuracy_score(Y, Y_pred)
        if log:
            with open('perceptron_accuracy.json', 'w') as fp:
                json.dump(accuracy, fp)
        if display_plot:
            epochs_, accuracy_ = zip(*accuracy.items())
            plt.plot(epochs_, accuracy_)
            plt.xlabel("Epochs")
            plt.ylabel("Train Accuracy")
            plt.show()
                    
    def predict(self, X):
        Y = []
        for x in X:
            result = self.perceptron(x)
            Y.append(int(result>=0))
        return np.array(Y)


class PerceptronWithSigmoid:
    
    def __init__(self):
        self.w = None
        self.b = None
        
    def perceptron(self, x):
        return np.sum(self.w * x) + self.b
    
    def sigmoid(self, z):
        return 1. / (1. + np.exp(-z))
    
    def grad_w(self, x, y):
        y_pred = self.sigmoid(self.perceptron(x))
        return (y_pred - y) * y_pred * (1 - y_pred) * x
    
    def grad_b(self, x, y):
        y_pred = self.sigmoid(self.perceptron(x))
        return (y_pred - y) * y_pred * (1 - y_pred)
    
    def fit(self, X, Y, epochs=10, learning_rate=0.01, log=False, display_plot=False):
        # initialise the weights and bias
        self.w = np.random.randn(1, X.shape[1])
        self.b = 0
        if log or display_plot: 
            #accuracy = {}
            mse = {}
        for i in tqdm_notebook(range(epochs), total=epochs, unit="epoch"):
            dw, db = 0, 0
            for x, y in zip(X, Y):
                dw += self.grad_w(x, y)
                db += self.grad_b(x, y)
            self.w -= learning_rate*dw
            self.b -= learning_rate*db
            
            if log or display_plot:
                Y_pred = self.predict(X)
                #Y_binarized = (Y >= SCALED_THRESHOLD).astype(np.int)
                #Y_pred_binarized = (Y_pred >= SCALED_THRESHOLD).astype(np.int)
                #accuracy[i] = accuracy_score(Y_binarized, Y_pred_binarized)
                mse[i] = mean_squared_error(Y, Y_pred)
        if log:
            #with open('perceptron_with_sigmoid_accuracy.json', 'w') as fp:
                #json.dump(accuracy, fp)
            with open('perceptron_with_sigmoid_mse.json', 'w') as fp:
                json.dump(mse, fp)
        if display_plot:
            #epochs_, accuracy_ = zip(*accuracy.items())
            #plt.plot(epochs_, accuracy_)
            #plt.xlabel("Epochs")
            #plt.ylabel("Train Accuracy")
            #plt.show()
            epochs_, mse_ = zip(*mse.items())
            plt.plot(epochs_, mse_)
            plt.xlabel("Epochs")
            plt.ylabel("Train Error (MSE)")
            plt.show()
            
                    
    def predict(self, X):
        Y = []
        for x in X:
            result = self.sigmoid(self.perceptron(x))
            Y.append(result)
        return np.array(Y)


