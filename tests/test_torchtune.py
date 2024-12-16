import unittest

import subprocess

class TestTorchtune(unittest.TestCase):
    def test_help(self):
        ret_code = subprocess.run(["tune", "--help"])
        self.assertEqual(0, ret_code.returncode)
        self.assertIsNone(ret_code.stderr)