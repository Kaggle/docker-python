import os
import unittest


class TestJupyterServer(unittest.TestCase):
    def test_version(self):
        from packaging.version import parse as parse_version
        from importlib.metadata import version as pckg_version

        self.assertTrue(parse_version(pckg_version("jupyter_server")) >= parse_version("2.0"))

    def test_terminals(self):
        import jupyter_server_terminals

        self.assertTrue(hasattr(jupyter_server_terminals, "version_info"))
