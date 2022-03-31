import subprocess
import unittest


class TestPythonLspServer(unittest.TestCase):
    def test_initialize(self):
        server = subprocess.Popen(
            'python -m pylsp --check-parent-process',
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)

        response = server.communicate(input=
            b'Content-Length: 67\r\n'
            b'Content-Type: application/vscode-jsonrpc; charset=utf8\r\n'
            b'\r\n'
            b'{"id": "a", "jsonrpc": "2.0", "method": "initialize", "params": {}}')[0]
        assert 'capabilities' in response.decode('utf-8')
