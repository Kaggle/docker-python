import unittest

import subprocess as sp

class TestStack(unittest.TestCase):
    def test_stack(self):
        try:
            proc = sp.Popen(["stack", "--version"], stdout = sp.PIPE, stderr = sp.PIPE)
            stdout, stderr = proc.communicate()
            self.assertEqual(proc.returncode, 0)
        except:
            self.assertTrue(False)
