import unittest
from packaging.version import parse
import kaggle_benchmarks

class TestKaggleBenchmarks(unittest.TestCase):
    def test_version(self):
        self.assertGreaterEqual(parse(kaggle_benchmarks.__version__), parse("0.6"))

    def test_core_imports(self):
        from kaggle_benchmarks import (
            Actor,
            ChatRoom,
            ExecutionMode,
            LLMChat,
            Participant,
            Run,
            Runs,
            Usage,
            benchmark,
            task,
        )
