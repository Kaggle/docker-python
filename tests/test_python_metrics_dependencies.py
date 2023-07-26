'''
Verifies that the packages used by the Python metrics orchestrator have valid versions

Please contact sohier@ or lipovetz@ if you need to push an update that would cause these tests to fail.
'''

import subprocess
import sys
import unittest

import numpy as np
import packaging.version
import pandas as pd


class TestLinuxDependencies(unittest.TestCase):
    '''
    Tests for the existence of all libraries the orchestrator calls via subprocess
    These APIs should be quite stable so we won't validate the exact versions
    '''
    def test_7z(self):
        result = subprocess.run('which 7z', shell=True, capture_output=True)
        assert len(result.stdout) > 0

    def test_gunzip(self):
        result = subprocess.run('which gunzip', shell=True, capture_output=True)
        assert len(result.stdout) > 0

    def test_ls(self):
        result = subprocess.run('which ls', shell=True, capture_output=True)
        assert len(result.stdout) > 0

    def test_pytest(self):
        result = subprocess.run('which pytest', shell=True, capture_output=True)
        assert len(result.stdout) > 0


class TestPythonDependencies(unittest.TestCase):
    '''
    Tests for the orchestrator's Python dependencies.
    All standard library imports should be covered by the python 3.10.x check.
    '''
    def test_python_version(self):
        # equivalent to py version == 3.10.x
        assert sys.version_info.major == 3
        assert sys.version_info.minor == 10

    def test_pandas_version(self):
        '''
        The python metrics team will need advance notice before a migration to Pandas 2.0.
        1.5 was the last 1.x release
        '''
        assert packaging.version.parse(pd.__version__) >= packaging.version.parse('1.5')
        assert packaging.version.parse(pd.__version__) < packaging.version.parse('2.0')

    def test_numpy_version(self):
        '''
        Numpy tends to be pretty stable so we'll accept a wider range of versions.
        '''
        assert packaging.version.parse(np.__version__) >= packaging.version.parse('1.23')
        assert packaging.version.parse(np.__version__) < packaging.version.parse('1.30')

    def test_packaging_version(self):
        assert packaging.version.parse(packaging.__version__) >= packaging.version.parse('21.0')

    def test_pytest_version(self):
        assert packaging.version.parse(packaging.__version__) >= packaging.version.parse('7.3')
        assert packaging.version.parse(packaging.__version__) < packaging.version.parse('8')
