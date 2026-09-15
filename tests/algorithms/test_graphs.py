import random
from typing import Hashable
import unittest
import networkx as nx

from dsa.graphs.graph_class import Graph, clone_networkx_graph



def make_random_graph(seed: int|None=None) -> nx.Graph[int]:
    rs = random.Random()
    rs.seed(seed)

    G = nx.erdos_renyi_graph(n=100, p=0.2, seed=seed)
    return G


class TestGraphs(unittest.TestCase):
    graph_pairs: list[tuple[nx.Graph, Graph]]

    def setUp(self) -> None:
        G_nx: nx.Graph[int] = make_random_graph()
        G: Graph[int] = clone_networkx_graph(G_nx)
        self.graph_pairs = [(G_nx, G)]

        return super().setUp()

    def check_graph_structure(self, G_nx: nx.Graph, G: Graph) -> None:
        self.assertSetEqual(set(G_nx.nodes()), set(G.nodes()))
        self.assertSetEqual(set(G_nx.edges()), set(G.edges()))

    def test_structure(self) -> None:
        for G_nx, G in self.graph_pairs:
            self.check_graph_structure(G_nx, G)