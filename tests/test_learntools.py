import unittest

from learntools.core import binder; binder.bind(globals())
from learntools.python.ex1 import *

class TestLearnTools(unittest.TestCase):
    def test_check(self):
        color="blue"
        q0.check()
