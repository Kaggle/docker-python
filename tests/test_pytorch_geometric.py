import unittest

import torch_cluster
import torch_sparse
import torch_scatter
from torch_geometric.data import Data
from torch_sparse import coalesce
import torch


class TestTorchGeometric(unittest.TestCase):
    def test_scatter(self):
        src = torch.tensor([[2, 0, 1, 4, 3], [0, 2, 1, 3, 4]])
        index = torch.tensor([[4, 5, 4, 2, 3], [0, 0, 2, 2, 1]])
        out, argmax = torch_scatter.scatter_max(src, index, fill_value=0)
        test_argmax = torch.LongTensor([[-1, -1,  3,  4,  0,  1],
                                        [ 1,  4,  3, -1, -1, -1]])
        test_out = torch.LongTensor([[0, 0, 4, 3, 2, 0],
                                     [2, 4, 3, 0, 0, 0]])
        self.assertTrue(torch.all(torch.eq(test_argmax, argmax)))
        self.assertTrue(torch.all(torch.eq(test_out, out)))

    def test_cluster(self):
        x = torch.Tensor([[-1, -1], [-1, 1], [1, -1], [1, 1]])
        batch = torch.tensor([0, 0, 0, 0])
        edge_index = torch_cluster.knn_graph(x, k=2, batch=batch, loop=False)
        test_edge_index = torch.LongTensor([[2, 1, 3, 0, 3, 0, 1, 2],
                                            [0, 0, 1, 1, 2, 2, 3, 3]])
        self.assertTrue(torch.all(torch.eq(test_edge_index, edge_index)))

    def test_sparse(self):
        index = torch.tensor([[1, 0, 1, 0, 2, 1],
                              [0, 1, 1, 1, 0, 0]])
        value = torch.Tensor([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7]])

        index, value = torch_sparse.transpose(index, value, 3, 2)
        test_index = torch.LongTensor([[0, 0, 1, 1],
                                       [1, 2, 0, 1]])
        test_value = torch.Tensor([[7., 9.], [5., 6.], [6., 8.], [3., 4.]])
        self.assertTrue(torch.all(torch.eq(test_index, index)))
        self.assertTrue(torch.all(torch.eq(test_value, value)))

    def test_spline_conv(self):
        #TODO !
        self.assertTrue(False)

    def test_geometric(self):
        x = torch.tensor([[1, 3, 5], [2, 4, 6]], dtype=torch.float).t()
        edge_index = torch.tensor([[0, 0, 1, 1, 2], [1, 1, 0, 2, 1]])
        data = Data(x=x, edge_index=edge_index).to(torch.device('cpu'))

        N = data.num_nodes

        self.assertTrue(data.x.tolist() == x.tolist())
        self.assertTrue(data['x'].tolist() == x.tolist())

        self.assertTrue(sorted(data.keys) == ['edge_index', 'x'])
        self.assertTrue(len(data) == 2)
        self.assertTrue('x' in data and 'edge_index' in data and 'pos' not in data)
        self.assertTrue(data.__cat_dim__('x', data.x) == 0)
        self.assertTrue(data.__cat_dim__('edge_index', data.edge_index) == -1)
        self.assertTrue(data.__inc__('x', data.x) == 0)
        self.assertTrue(data.__inc__('edge_index', data.edge_index) == data.num_nodes)
        data.contiguous()
        self.assertTrue(data.x.is_contiguous())

        data.edge_index, _ = coalesce(data.edge_index, None, N, N)
        data = data.coalesce()
        self.assertTrue(data.is_coalesced())

        clone = data.clone()
        self.assertTrue(clone != data)
        self.assertTrue(len(clone) == len(data))
        self.assertTrue(clone.x.tolist() == data.x.tolist())
        self.assertTrue(clone.edge_index.tolist() == data.edge_index.tolist())

        data['x'] = x + 1
        self.assertTrue(data.x.tolist() == (x + 1).tolist())

        self.assertTrue(data.__repr__() == 'Data(edge_index=[2, 4], x=[3, 2])')

        dictionary = {'x': data.x, 'edge_index': data.edge_index}
        data = Data.from_dict(dictionary)
        self.assertTrue(sorted(data.keys) == ['edge_index', 'x'])

        self.assertTrue(data.is_undirected())

        self.assertTrue(data.num_nodes == 3)
        self.assertTrue(data.num_edges == 4)
        self.assertTrue(data.num_faces is None)
        self.assertTrue(data.num_node_features == 2)
        self.assertTrue(data.num_features == 2)
