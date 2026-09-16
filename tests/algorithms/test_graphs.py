import unittest
from typing import Hashable, Iterator, Protocol

import networkx as nx

from dsa.graphs import pathfinding, random_graphs
from dsa.graphs.exceptions import NoPathError
from dsa.graphs.graph_class import Graph
from dsa.utils.randomization import RandomSeeder, make_random_state


class PathFinder(Protocol):
    def __call__[N: Hashable](self, G: Graph[N], source: N, target: N) -> int|float: ...


def iterate_random_pair_dists(
        G: nx.Graph,
        n: int=20,
        seed: RandomSeeder|None=None
        ) -> Iterator[tuple[int, int, int|float|None]]:
    rs = make_random_state(seed)
    nodes = list(G.nodes())
    for _ in range(n):
        u, v = rs.choices(nodes, k=2)

        try:
            dist = nx.bellman_ford_path_length(G, source=u, target=v)
        except nx.NetworkXNoPath:
            dist = None
        yield u, v, dist


class TestGraphs(unittest.TestCase):
    graph_pairs: list[tuple[Graph, nx.Graph]]

    def setUp(self) -> None:
        graphs: list[Graph] = [random_graphs.erdos_renyi(n=100, p=0.2, seed=0)]
        self.graph_pairs = [(G, G.to_networkx()) for G in graphs]

        return super().setUp()

    def check_graph_structure(self, G: Graph, G_nx: nx.Graph) -> None:
        # Check that the two graphs have the same nodes and edges
        self.assertSetEqual(set(G_nx.nodes()), set(G.nodes()))
        self.assertSetEqual(set(G_nx.edges()), set(G.edges()))

        # Check that every node has the same set of neighbors
        for node in G.nodes():
            a = set(G.neighbors(node))
            b = set(G_nx.neighbors(node))
            self.assertSetEqual(a, b)

    def test_structure(self) -> None:
        for G, G_nx in self.graph_pairs:
            self.check_graph_structure(G, G_nx)

            
class TestPathFinding(unittest.TestCase):
    graph_pairs: list[tuple[Graph, nx.Graph]]

    def setUp(self) -> None:
        self.rs = make_random_state(0)
        graphs: list[Graph] = [
            random_graphs.erdos_renyi(n=100, p=0.02, seed=self.rs),
            random_graphs.erdos_renyi(n=100, p=0.5, seed=self.rs, weights=lambda: self.rs.randint(0, 20))
        ]
        self.graph_pairs = [(G, G.to_networkx()) for G in graphs]
        
        return super().setUp()

    def check_find_shortest_path(self, pathfinder: PathFinder) -> None:
        for i, (G, G_nx) in enumerate(self.graph_pairs):
            for u, v, dist in iterate_random_pair_dists(G_nx, seed=self.rs):
                
                if dist is None:
                    with self.assertRaises(NoPathError):
                        pathfinder(G, u, v)
                else:
                    shortest_found = pathfinder(G, u, v)
                    self.assertEqual(shortest_found, dist)

    def test_dijkstra(self) -> None:
        self.check_find_shortest_path(pathfinding.shortest_path_dijkstra)
