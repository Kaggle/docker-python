import unittest

import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader, TensorDataset

import flash


class DummyDataset(torch.utils.data.Dataset):

    def __init__(self, predict: bool = False):
        self._predict = predict

    def __getitem__(self, index: int):
        return torch.rand(1, 28, 28), torch.randint(10, size=(1, )).item()

    def __len__(self) -> int:
        return 10


class DummyClassifier(nn.Module):

    def __init__(self):
        super().__init__()
        self.backbone = nn.Sequential(nn.Flatten(), nn.Linear(28 * 28, 10))
        self.head = nn.LogSoftmax()

    def forward(self, x):
        return self.head(self.backbone(x))


class TestLightningFlash(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(flash.__version__)

    def test_task_fit(self):
        model = nn.Sequential(nn.Flatten(), nn.Linear(28 * 28, 10), nn.LogSoftmax())
        train_dl = torch.utils.data.DataLoader(DummyDataset())
        val_dl = torch.utils.data.DataLoader(DummyDataset())
        task = flash.ClassificationTask(model, F.nll_loss)
        trainer = flash.Trainer(gpus=None, max_epochs=1)
        result = trainer.fit(task, train_dl, val_dl)
        self.assertTrue(result)
