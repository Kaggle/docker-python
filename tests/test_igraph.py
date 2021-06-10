import unittest

from igraph import Graph


class TestIgraph(unittest.TestCase):
    def test_graph(self):
        # Create a graph with 10 vertices & 2 children each.
        g2 = Graph.Tree(n=10, children=2) 
       
        self.assertEqual(9, len(g2.get_edgelist()))

