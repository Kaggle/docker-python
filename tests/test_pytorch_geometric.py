import unittest

import torch
import torch_cluster
import torch_geometric
import torch_sparse
import torch_scatter

from torch_geometric.data import Data
from torch_sparse import coalesce
from torch_geometric.nn import SplineConv


class TestTorchGeometric(unittest.TestCase):
    def setUp(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def test_scatter(self):
        src = torch.tensor([[2, 0, 1, 4, 3], [0, 2, 1, 3, 4]]).to(self.device)
        index = torch.tensor([[4, 5, 4, 2, 3], [0, 0, 2, 2, 1]]).to(self.device)
        out, argmax = torch_scatter.scatter_max(src, index, fill_value=0)
        test_argmax = torch.LongTensor([[-1, -1,  3,  4,  0,  1],
                                        [ 1,  4,  3, -1, -1, -1]]).to(self.device)
        test_out = torch.LongTensor([[0, 0, 4, 3, 2, 0],
                                     [2, 4, 3, 0, 0, 0]]).to(self.device)
        self.assertTrue(torch.all(torch.eq(test_argmax, argmax)))
        self.assertTrue(torch.all(torch.eq(test_out, out)))

    def test_cluster(self):
        x = torch.Tensor([[-1, -1], [-1, 1], [1, -1], [1, 1]]).to(self.device)
        batch = torch.tensor([0, 0, 0, 0]).to(self.device)
        edge_index = torch_cluster.knn_graph(x, k=2, batch=batch, loop=False).to(self.device)
        test_edge_index = torch.LongTensor([[2, 1, 3, 0, 3, 0, 1, 2],
                                            [0, 0, 1, 1, 2, 2, 3, 3]]).to(self.device)
        edge_list = edge_index.tolist()
        test_edge_list = test_edge_index.tolist()
        del edge_index, test_edge_index
        # need to transpose the edges to (ei, ej) format
        edge_list = [(edge_list[0][i], edge_list[1][i]) for i in range(len(edge_list[0]))]
        test_edge_list = [(test_edge_list[0][i], test_edge_list[1][i]) for i in range(len(test_edge_list[0]))]
        self.assertCountEqual(edge_list, test_edge_list)

    def test_sparse(self):
        index = torch.tensor([[1, 0, 1, 0, 2, 1],
                              [0, 1, 1, 1, 0, 0]]).to(self.device)
        value = torch.Tensor([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7]]).to(self.device)

        index, value = torch_sparse.transpose(index, value, 3, 2)
        test_index = torch.LongTensor([[0, 0, 1, 1],
                                       [1, 2, 0, 1]]).to(self.device)
        test_value = torch.Tensor([[7., 9.], [5., 6.], [6., 8.], [3., 4.]]).to(self.device)
        self.assertTrue(torch.all(torch.eq(test_index, index)))
        self.assertTrue(torch.all(torch.eq(test_value, value)))

    def test_spline_conv(self):
        in_channels, out_channels = (16, 32)
        edge_index = torch.tensor([[0, 0, 0, 1, 2, 3], [1, 2, 3, 0, 0, 0]]).to(self.device)
        num_nodes = edge_index.max().item() + 1
        x = torch.randn((num_nodes, in_channels)).to(self.device)
        pseudo = torch.rand((edge_index.size(1), 3)).to(self.device)

        conv = SplineConv(in_channels, out_channels, dim=3, kernel_size=5).to(self.device)
        self.assertEqual('SplineConv(16, 32)', conv.__repr__())
        with torch_geometric.debug():
            self.assertEqual((num_nodes, out_channels), conv(x, edge_index, pseudo).size())

    def test_geometric(self):
        x = torch.tensor([[1, 3, 5], [2, 4, 6]], dtype=torch.float).t().to(self.device)
        edge_index = torch.tensor([[0, 0, 1, 1, 2], [1, 1, 0, 2, 1]]).to(self.device)
        data = Data(x=x, edge_index=edge_index).to(torch.device('cpu'))

        N = data.num_nodes

        self.assertCountEqual(data.x.tolist(), x.tolist())
        self.assertCountEqual(data['x'].tolist(), x.tolist())

        self.assertEqual(['edge_index', 'x'], sorted(data.keys))
        self.assertEqual(2, len(data))
        self.assertIn('x', data)
        self.assertIn('edge_index', data)
        self.assertNotIn('pos', data)        
        self.assertEqual(0, data.__cat_dim__('x', data.x))
        self.assertEqual(-1, data.__cat_dim__('edge_index', data.edge_index))
        self.assertEqual(0, data.__inc__('x', data.x))
        self.assertEqual(data.num_nodes, data.__inc__('edge_index', data.edge_index))
        data.contiguous()
        self.assertTrue(data.x.is_contiguous())

        data.edge_index, _ = coalesce(data.edge_index, None, N, N)
        data = data.coalesce()
        self.assertTrue(data.is_coalesced())

        clone = data.clone()
        self.assertNotEqual(clone, data)
        self.assertEqual(len(clone), len(data))
        self.assertCountEqual(clone.x.tolist(), data.x.tolist())
        self.assertCountEqual(clone.edge_index.tolist(), data.edge_index.tolist())

        data['x'] = x + 1
        self.assertCountEqual(data.x.tolist(), (x + 1).tolist())

        self.assertEqual('Data(edge_index=[2, 4], x=[3, 2])', data.__repr__())

        dictionary = {'x': data.x, 'edge_index': data.edge_index}
        data = Data.from_dict(dictionary)
        self.assertEqual(['edge_index', 'x'], sorted(data.keys))

        self.assertTrue(data.is_undirected())

        self.assertEqual(3, data.num_nodes)
        self.assertEqual(4, data.num_edges)
        self.assertIsNone(data.num_faces)
        self.assertEqual(2, data.num_node_features)
        self.assertEqual(2, data.num_features)