import unittest

import parse

class TestParse(unittest.TestCase):
    
    def test_parse(self):
        parse.parse("It's {}, I love it!", "It's spam, I love it!")
        parse.search('Age: {:d}\n', 'Name: Rufus\nAge: 42\nColor: red\n')