import unittest
from dataclasses import dataclass, field
from functools import cache, partial
from typing import Any, Callable, Hashable, Iterable, Iterator, Protocol

import networkx as nx

from dsa.graphs import pathfinding, random_graphs
from dsa.graphs.exceptions import CycleError, NoPathError
from dsa.graphs.graph_class import DiGraph, Graph
from dsa.utils.randomization import RandomSeeder, make_random_state


@dataclass
class Case[N]:
    """This just holds some graph that we want to run some tests on, and exposes stuff
    like the equivalent networkx graph, and shortest distances"""

    title: str
    G: Graph[N]
    G_nx: nx.Graph[N] = field(init=False)
    dists: dict[N, dict[N, int|float]] = field(init=False)

    def __post_init__(self) -> None:
        self.G_nx = self.G.to_networkx()
        self.dists = {u: d for u, d in nx.all_pairs_bellman_ford_path_length(self.G_nx)}


class PathFinder(Protocol):
    """Protocol for a callable which finds some path given source"""
    def __call__[N: Hashable](self, G: Graph[N], source: N, target: N) -> list[N]: ...


def _iterate_random_pairs[N](nodes: Iterable[N], n: int=20, seed: RandomSeeder|None=None) -> Iterator[tuple[N, N]]:
    """Iterate over random pairs of elements from the input list"""
    rs = make_random_state(seed)
    nodes_ = list(nodes)

    for _ in range(n):
        u, v = rs.choices(nodes_, k=2)
        yield u, v


def standard_networks(n: int, seed: RandomSeeder) -> Iterator[Case[int]]:
    """Produces some typical graphs which can be re-used for various tests"""

    rs = make_random_state(seed)

    chain_edges = [(i, i+1) for i in range(5)]
    yield Case("Chain, undirected", Graph(edges=chain_edges))
    yield Case("Chain, directed", DiGraph(edges=chain_edges))
    yield Case("Chain, directed+weighted", DiGraph(edges=((u, v, rs.randint(1, 10)) for u, v in chain_edges)))

    # Erdos-renyi graph
    yield Case("ER graph", random_graphs.erdos_renyi(n=n, p=0.2, seed=rs))
    # Sparse ER graph
    yield Case("Sparse ER", random_graphs.erdos_renyi(n=n, p=0.02, seed=rs))
    # Weighted ER
    yield Case("Weighted ER", random_graphs.erdos_renyi(n=n, p=0.5, seed=rs, weights=lambda: rs.randint(0, 20)))
    # Directed ER
    yield Case("Directed ER", random_graphs.erdos_renyi(n=n, p=0.3, seed=rs, directed=True))

    # Barabasi-Albert graph
    yield Case("BA graph", random_graphs.barabasi_albert(n=n, m=max(1, n // 5), seed=rs))

    # Graph with a self-edge
    yield Case("Graph w. self-edge", Graph(nodes=[1,2,3]).add_edge(1, 1, weight=1))
    yield Case("Digraph with self-edge", DiGraph(nodes=[1,2,3]).add_edge(1, 1, weight=1))


@cache
def cases(n: int=50, seed: RandomSeeder=0) -> list[Case[int]]:
    res = list(standard_networks(n=n, seed=seed))
    return res


class TestGraphs(unittest.TestCase):
    cases: list[Case[int]]

    def setUp(self) -> None:
        self.cases = cases()

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
        for case in self.cases:
            self.check_graph_structure(case.G, case.G_nx)

    def test_edge_view(self) -> None:
        """Check that edge views behave as expected"""
        for case in self.cases:
            edges = case.G.edges()
            n = len(edges)
            n_brute = sum(1 for _ in edges)
            self.assertEqual(n, n_brute)

            
class TestPathFinding(unittest.TestCase):
    cases: list[Case[int]]

    def setUp(self) -> None:
        self.rs = make_random_state(0)
        self.cases = cases()
        
        return super().setUp()

    def check_find_shortest_path(self, pathfinder: PathFinder) -> None:
        for case in self.cases:
            for u, v in _iterate_random_pairs(list(case.G.nodes()), seed=self.rs):
                dist = case.dists[u].get(v)
                if dist is None:
                    with self.assertRaises(NoPathError):
                        pathfinder(case.G, u, v)
                else:
                    path = pathfinder(case.G, u, v)
                    shortest_found = case.G.compute_path_length(path)
                    self.assertEqual(shortest_found, dist, msg=f"Error in case {case.title}")

    def test_dijkstra(self) -> None:
        self.check_find_shortest_path(pathfinding.dijkstra_path)

        # Find the shortest path (or one of them) for some connected pairs, and check the path length
        for case in self.cases:
            # Only test some random connected pairs so the tests don't take forever
            checks = [(u, v, dist_) for u, d in case.dists.items() for v, dist_ in d.items()]
            selected = self.rs.choices(checks, k=20)
            for u, v, dist in selected:
                path = pathfinding.dijkstra_path(case.G, source=u, target=v)
                path_length = case.G.compute_path_length(path)
                self.assertEqual(path_length, dist)

    def test_a_star(self) -> None:
        pathfinder = partial(pathfinding.a_star, heuristic=lambda n: 0)
        self.check_find_shortest_path(pathfinder)

    def test_bellman_ford(self) -> None:
        self.check_find_shortest_path(pathfinding.bellman_ford_path)
        func = partial(pathfinding.bellman_ford_path, source=0, target=1)
        self.check_detects_negative_cycle(func)

    def check_detects_negative_cycle(self, func: Callable[[Graph], Any]) -> None:
        G = random_graphs.barabasi_albert(n=10, m=2, seed=0)
        G.add_edge(0, 1, weight=0)
        G.add_edge(1, 0, weight=-1)

        with self.assertRaises(CycleError):
            func(G)

    def test_single_source_dijkstra(self) -> None:
        for case in self.cases:
            for source in case.G.nodes():
                dists_correct = case.dists[source]
                dists_found = pathfinding.single_source_dijkstra_path_lengths(case.G, source=source)
                self.assertDictEqual(dists_found, dists_correct)

    def test_single_target_dijkstra(self) -> None:
        for case in self.cases:
            correct: dict[int, dict[int, int|float]] = {u: {} for u in case.G.nodes()}
            for u, dists in case.dists.items():
                for v, dist in dists.items():
                    correct[v][u] = dist

            for target in case.G.nodes():
                dists_found = pathfinding.single_target_dijkstra_path_lengths(case.G, target=target)
                self.assertDictEqual(dists_found, correct[target])

    def test_has_path(self) -> None:
        for case in self.cases:
            nodes = list(case.G.nodes())
            if len(nodes) < 2:
                continue
            for _ in range(20):
                u, v = self.rs.choices(nodes, k=2)
                expected = nx.has_path(case.G_nx, source=u, target=v)
                found = pathfinding.has_path(case.G, source=u, target=v)
                self.assertIs(found, expected)

    def test_floyd_warshall(self) -> None:
        for case in self.cases:
            print(case.title)  # !!!
            dists = pathfinding.floyd_warshall(case.G)
            self.assertDictEqual(dists, case.dists)

        self.check_detects_negative_cycle(pathfinding.floyd_warshall)
