import unittest
import collections
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms

import catalyst
from catalyst.dl import SupervisedRunner, CheckpointCallback
from catalyst import utils
from safitty import Safict


def _to_categorical(y, num_classes=None, dtype='float32'):
    """
    Taken from 
    github.com/keras-team/keras/blob/master/keras/utils/np_utils.py
    Converts a class vector (integers) to binary class matrix.
    E.g. for use with categorical_crossentropy.
    # Arguments
        y: class vector to be converted into a matrix
            (integers from 0 to num_classes).
        num_classes: total number of classes.
        dtype: The data type expected by the input, as a string
            (`float32`, `float64`, `int32`...)
    # Returns
        A binary matrix representation of the input. The classes axis
        is placed last.
    # Example
    ```python
    # Consider an array of 5 labels out of a set of 3 classes {0, 1, 2}:
    > labels
    array([0, 2, 1, 2, 0])
    # `to_categorical` converts this into a matrix with as many
    # columns as there are classes. The number of rows
    # stays the same.
    > to_categorical(labels)
    array([[ 1.,  0.,  0.],
           [ 0.,  0.,  1.],
           [ 0.,  1.,  0.],
           [ 0.,  0.,  1.],
           [ 1.,  0.,  0.]], dtype=float32)
    ```
    """

    y = np.array(y, dtype='int')
    input_shape = y.shape
    if input_shape and input_shape[-1] == 1 and len(input_shape) > 1:
        input_shape = tuple(input_shape[:-1])
    y = y.ravel()
    if not num_classes:
        num_classes = np.max(y) + 1
    n = y.shape[0]
    categorical = np.zeros((n, num_classes), dtype=dtype)
    categorical[np.arange(n), y] = 1
    output_shape = input_shape + (num_classes,)
    categorical = np.reshape(categorical, output_shape)
    return categorical


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 20, 5, 1)
        self.conv2 = nn.Conv2d(20, 50, 5, 1)
        self.fc1 = nn.Linear(4 * 4 * 50, 500)
        self.fc2 = nn.Linear(500, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        x = x.view(-1, 4 * 4 * 50)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


class TestCatalyst(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(catalyst.__version__)
    
    def test_mnist(self):
        utils.set_global_seed(42)
        x_train = np.random.random((100, 1, 28, 28)).astype(np.float32)
        y_train = _to_categorical(
            np.random.randint(10, size=(100, 1)), 
            num_classes=10
        ).astype(np.float32)
        x_valid = np.random.random((20, 1, 28, 28)).astype(np.float32)
        y_valid = _to_categorical(
            np.random.randint(10, size=(20, 1)), 
            num_classes=10
        ).astype(np.float32)

        x_train, y_train, x_valid, y_valid = \
            list(map(torch.tensor, [x_train, y_train, x_valid, y_valid]))

        bs = 32
        num_workers = 4
        data_transform = transforms.ToTensor()

        loaders = collections.OrderedDict()

        trainset = torch.utils.data.TensorDataset(x_train, y_train)
        trainloader = torch.utils.data.DataLoader(
            trainset, batch_size=bs,
            shuffle=True, num_workers=num_workers)

        validset = torch.utils.data.TensorDataset(x_valid, y_valid)
        validloader = torch.utils.data.DataLoader(
            validset, batch_size=bs,
            shuffle=False, num_workers=num_workers)

        loaders["train"] = trainloader
        loaders["valid"] = validloader

        # experiment setup
        num_epochs = 3
        logdir = "./logs"

        # model, criterion, optimizer
        model = Net()
        criterion = nn.BCEWithLogitsLoss()
        optimizer = torch.optim.Adam(model.parameters())

        # model runner
        runner = SupervisedRunner()

        # model training
        runner.train(
            model=model,
            criterion=criterion,
            optimizer=optimizer,
            loaders=loaders,
            logdir=logdir,
            num_epochs=num_epochs,
            verbose=False,
            callbacks=[CheckpointCallback(save_n_best=3)]
        )
        
        metrics = Safict.load("./logs/checkpoints/_metrics.json")
        metrics_flag1 = \
            metrics.get("train.3", "loss") < metrics.get("train.1", "loss")
        metrics_flag2 = metrics.get("best", "loss") < 0.35
        self.assertTrue(metrics_flag1)
        self.assertTrue(metrics_flag2)
