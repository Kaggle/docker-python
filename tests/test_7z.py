import subprocess
import unittest


class Test7z(unittest.TestCase):
    def test_basic(self):
        result = subprocess.run('which 7z', shell=True, capture_output=True)
        assert len(result.stdout) > 0
