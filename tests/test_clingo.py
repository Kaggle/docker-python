import unittest

from clingo import Control

class TestClingo(unittest.TestCase):
    def test_solve(self):
        cc = Control()

        cc.add('base', [], '''
        a(X) :- not b(X), d(X).
        b(X) :- not a(X), d(X).''')
        cc.add('base', [], "d(1;2;3).")
        cc.ground([("base",[])])

        out = {}
        def onmodel(m):
            out['out'] = str(m)
        cc.solve(on_model = onmodel)

        self.assertEqual('d(1) d(2) d(3) b(1) b(2) b(3)', out['out'])
