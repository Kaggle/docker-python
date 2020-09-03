import unittest

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

import pytorch_lightning as pl
from pytorch_lightning.metrics.functional import to_onehot


class LitDataModule(pl.LightningDataModule):

    def __init__(self, batch_size=16):
        super().__init__()

        self.batch_size = batch_size

    def setup(self, stage=None):
        X_train = torch.rand(100, 1, 28, 28).float()
        y_train = to_onehot(torch.randint(0, 10, size=(100,)), num_classes=10).float()
        X_valid = torch.rand(20, 1, 28, 28)
        y_valid = to_onehot(torch.randint(0, 10, size=(20,)), num_classes=10).float()

        self.train_ds = TensorDataset(X_train, y_train)
        self.valid_ds = TensorDataset(X_valid, y_valid)

    def train_dataloader(self):
        return DataLoader(self.train_ds, batch_size=self.batch_size, shuffle=True)

    def val_dataloader(self):
        return DataLoader(self.valid_ds, batch_size=self.batch_size, shuffle=False)


class LitClassifier(pl.LightningModule):

    def __init__(self):
        super().__init__()
        self.l1 = torch.nn.Linear(28 * 28, 10)

    def forward(self, x):
        return torch.relu(self.l1(x.view(x.size(0), -1)))

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = F.binary_cross_entropy_with_logits(y_hat, y)
        result = pl.TrainResult(loss)
        result.log('train_loss', loss, on_epoch=True)
        return result

    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = F.binary_cross_entropy_with_logits(y_hat, y)
        result = pl.EvalResult(checkpoint_on=loss)
        result.log('val_loss', loss)
        return result

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.02)


class TestPytorchLightning(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(pl.__version__)

    def test_mnist(self):
        dm = LitDataModule()
        model = LitClassifier()
        trainer = pl.Trainer(gpus=None, max_epochs=1)
        result = trainer.fit(model, datamodule=dm)
        self.assertTrue(result)
