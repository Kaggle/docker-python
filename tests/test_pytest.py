
import subprocess
import unittest


class test_pytest(unittest.TestCase):
    def test_pytest_on_pandas_test(self):
        cmd = 'pytest /input/tests/test_pandas.py'
        result = subprocess.run(cmd, shell=True, capture_output=True)
        self.assertEqual(result.returncode, 0)
