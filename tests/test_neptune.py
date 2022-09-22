import unittest

try:
    # neptune-client=0.9.0+ package structure
    import neptune.new as neptune
except ImportError:
    # neptune-client>=1.0.0 package structure
    import neptune


class TestNeptune(unittest.TestCase):
    def test_version(self):
        self.assertIsNotNone(neptune.__version__)

    def test_init_offline_run(self):
        run = neptune.init(mode="offline")
        run["foo"] = "bar"
        run["baz"].log(42)
        self.assertTrue("foo" in run.get_structure())
        self.assertTrue("baz" in run.get_structure())


