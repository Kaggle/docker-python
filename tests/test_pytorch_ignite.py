import unittest

from ignite.engine import Engine


class TestPytorchIgnite(unittest.TestCase):
    def test_engine(self):

        def update_fn(engine, batch):
            pass

        engine = Engine(update_fn)
        engine.run([0, 1, 2])
