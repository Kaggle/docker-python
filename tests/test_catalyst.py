import unittest
import collections

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms

import catalyst
from catalyst.dl import SupervisedRunner, CheckpointCallback
from safitty import Safict


class TestCatalyst(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(catalyst.__version__)
    
    def test_mnist(self):
        bs = 32
        num_workers = 4

        data_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307, ), (0.3081, ))
        ])


        loaders = collections.OrderedDict()

        trainset = torchvision.datasets.MNIST(
            root='./data', train=False,
            download=True, transform=data_transform)
        trainloader = torch.utils.data.DataLoader(
            trainset, batch_size=bs,
            shuffle=True, num_workers=num_workers)

        testset = trainset
        testloader = torch.utils.data.DataLoader(
            testset, batch_size=bs,
            shuffle=False, num_workers=num_workers)

        loaders["train"] = trainloader
        loaders["valid"] = testloader
        
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

        # experiment setup
        num_epochs = 3
        logdir = "./logs"

        # model, criterion, optimizer
        model = Net()
        criterion = nn.CrossEntropyLoss()
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
            metrics.get("train.2", "loss") < metrics.get("train.0", "loss")
        metrics_flag2 = metrics.get("train.2", "loss") < 0.05
        self.assertTrue(metrics_flag1)
        self.assertTrue(metrics_flag2)
