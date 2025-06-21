import unittest
import subprocess
import re


# Remove ANSI coloring escape codes
def strip_ansi(text):
    ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", text)


class TestAnyWidget(unittest.TestCase):

    def test_labextension(self):
        output = subprocess.check_output(
            ["jupyter", "labextension", "list"], stderr=subprocess.STDOUT, text=True
        )
        output = strip_ansi(output)
        match = re.search(r"^\s*anywidget\s+v[\d.]+\s+enabled\s+OK\b.*$", output, re.MULTILINE)
        self.assertIsNotNone(match, "anywidget not found in labextension list")
