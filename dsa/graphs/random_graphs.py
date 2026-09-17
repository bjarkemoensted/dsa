"""Tooling for initializing various random graphs"""


from typing import Callable, Iterator, Sequence

from dsa.graphs.graph_class import DEFAULT_EDGE_WEIGHT, Graph, DiGraph
from dsa.utils.randomization import RandomSeeder, make_random_state

type WeightGenerator = Callable[[], float|int]


def iter_links[N](nodes: Sequence[N], directed: bool) -> Iterator[tuple[N, N]]:
    edges = ((nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i+1, len(nodes)))
    for u, v in edges:
        yield u, v
        if directed:
            yield v, u


def erdos_renyi(
        n: int,
        p: float,
        seed: RandomSeeder=None,
        weights: WeightGenerator|float|int=DEFAULT_EDGE_WEIGHT,
        directed: bool=False
        ) -> Graph:
    """Generates an Erdős-Rényi random graph.
    n: Number of nodes
    p: the probability of realization of an edge (u, v).
    seed: None, int, or random.Random object. None/int will be converted into a Random object.
    weights: Callable for generating random edge weights, or int/float for constant weights"""

    if not (0.0 <= p <= 1.0):
        raise ValueError(f"p must be in the unit interval - got {p!r}")
    # Initialise a graph with n nodes
    nodes = list(range(n))
    cls_ = DiGraph if directed else Graph
    G = cls_(nodes=nodes)

    # Add edges
    rs = make_random_state(seed)
    for u, v in iter_links(nodes, directed):
        # Skip if random uniform variable r > p
        if rs.uniform(0.0, 1.0) > p:
            continue
        # Determine weight an add edge
        weight = weights() if callable(weights) else weights
        G.add_edge(u, v, weight)

    return G


def barabasi_albert(
        n: int,
        m: int,
        seed: RandomSeeder=None,
        weights: WeightGenerator|float|int=DEFAULT_EDGE_WEIGHT,
        ) -> Graph:

    rs = make_random_state(seed)
    import networkx as nx
    G = nx.Graph()
    G.degree
    raise NotImplementedError