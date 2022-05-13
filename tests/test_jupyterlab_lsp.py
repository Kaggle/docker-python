import os
import unittest

from jupyter_server.serverapp import ServerApp

# Adapted from:
# https://github.com/jupyter-lsp/jupyterlab-lsp/blob/ce76fab170feea506faf9ef47e4bd6a468c24313/python_packages/jupyter_lsp/jupyter_lsp/tests/test_extension.py
class TestJupyterLabLsp(unittest.TestCase):
    def test_serverextension_path(self):
        import jupyter_lsp
        paths = jupyter_lsp._jupyter_server_extension_paths()
        for path in paths:
            self.assertTrue(__import__(path["module"]))


    def test_serverextension(self):
        app = ServerApp()
        app.initialize(
            ["--ServerApp.jpserver_extensions={'jupyter_lsp.serverextension': True}"],
            new_httpserver=False,
        )
        self.assertTrue(app.language_server_manager)

        found_lsp = False
        for r in app.web_app.default_router.rules:
            for rr in r.target.rules:
                if "/lsp/" in str(rr.matcher.regex):
                    found_lsp = True

        self.assertTrue(found_lsp, "didn't install the /lsp/ route")

