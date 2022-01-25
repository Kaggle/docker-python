import unittest

import pytorch_lightning as pl
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset


class LitDataModule(pl.LightningDataModule):

    def __init__(self, batch_size=16):
        super().__init__()

        self.batch_size = batch_size

    def setup(self, stage=None):
        X_train = torch.rand(100, 1, 28, 28)
        y_train = torch.randint(0, 10, size=(100,))
        X_valid = torch.rand(20, 1, 28, 28)
        y_valid = torch.randint(0, 10, size=(20,))

        self.train_ds = TensorDataset(X_train, y_train)
        self.valid_ds = TensorDataset(X_valid, y_valid)

    def train_dataloader(self):
        return DataLoader(self.train_ds, batch_size=self.batch_size, shuffle=True, num_workers=1)

    def val_dataloader(self):
        return DataLoader(self.valid_ds, batch_size=self.batch_size, shuffle=False, num_workers=1)


class LitClassifier(pl.LightningModule):

    def __init__(self):
        super().__init__()
        self.l1 = torch.nn.Linear(28 * 28, 10)

    def forward(self, x):
        return F.relu(self.l1(x.view(x.size(0), -1)))

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = F.cross_entropy(y_hat, y)
        self.log('train_loss', loss)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = F.cross_entropy(y_hat, y)
        self.log('val_loss', loss)

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=1e-2)

class TestPytorchLightning(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(pl.__version__)

    def test_mnist(self):
        dm = LitDataModule()
        model = LitClassifier()
        trainer = pl.Trainer(gpus=None, max_epochs=1)
        trainer.fit(model, datamodule=dm)

        self.assertIn("train_loss", trainer.logged_metrics)
        self.assertIn("val_loss", trainer.logged_metrics)
        
