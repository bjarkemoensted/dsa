import unittest
from typing import Hashable, Iterator, Protocol

import networkx as nx

from dsa.graphs import pathfinding, random_graphs
from dsa.graphs.exceptions import NoPathError
from dsa.graphs.graph_class import Graph, DiGraph
from dsa.utils.randomization import RandomSeeder, make_random_state


class PathFinder(Protocol):
    def __call__[N: Hashable](self, G: Graph[N], source: N, target: N) -> int|float: ...


def iterate_random_pair_dists(
        G: nx.Graph,
        n: int=20,
        seed: RandomSeeder|None=None
        ) -> Iterator[tuple[int, int, int|float|None]]:
    """Given a graph, iterates over random pairs of nodes u, v, and the shortest distance from u to v."""

    rs = make_random_state(seed)
    nodes = list(G.nodes())
    for _ in range(n):
        u, v = rs.choices(nodes, k=2)

        try:
            dist = nx.bellman_ford_path_length(G, source=u, target=v)
        except nx.NetworkXNoPath:
            dist = None
        yield u, v, dist


def standard_networks(n: int, seed: RandomSeeder) -> Iterator[Graph]:
    """Produces some typical graphs which can be re-used for various tests"""

    rs = make_random_state(seed)
    # Erdos-renyi graph
    yield random_graphs.erdos_renyi(n=n, p=0.2, seed=rs)
    # Sparse ER graph
    yield random_graphs.erdos_renyi(n=n, p=0.02, seed=rs)
    # Weighted ER
    yield random_graphs.erdos_renyi(n=n, p=0.5, seed=rs, weights=lambda: rs.randint(0, 20))
    # Directed ER
    yield random_graphs.erdos_renyi(n=n, p=0.3, seed=rs, directed=True)

    # Graph with a self-edge
    yield Graph(nodes=[1,2,3]).add_edge(1, 1, weight=1)
    yield DiGraph(nodes=[1,2,3]).add_edge(1, 1, weight=1)


def cases(n: int=100, seed: RandomSeeder=0) -> list[tuple[Graph, nx.Graph]]:
    res = [(G, G.to_networkx()) for G in standard_networks(n=n, seed=seed)]
    return res


class TestGraphs(unittest.TestCase):
    graph_pairs: list[tuple[Graph, nx.Graph]]

    def setUp(self) -> None:
        self.graph_pairs = cases()

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

    def test_edge_view(self) -> None:
        """Check that edge views behave as expected"""
        for G, _ in self.graph_pairs:
            edges = G.edges()
            n = len(edges)
            n_brute = sum(1 for _ in edges)
            self.assertEqual(n, n_brute)

            
class TestPathFinding(unittest.TestCase):
    graph_pairs: list[tuple[Graph, nx.Graph]]

    def setUp(self) -> None:
        self.rs = make_random_state(0)
        self.graph_pairs = cases()
        
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
