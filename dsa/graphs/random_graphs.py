"""Tooling for initializing various random graphs"""


from typing import Callable

from dsa.graphs.graph_class import DEFAULT_EDGE_WEIGHT, Graph
from dsa.utils.randomization import RandomSeeder, make_random_state

type WeightGenerator = Callable[[], float|int]


def erdos_renyi(
        n: int,
        p: float,
        seed: RandomSeeder=None,
        weights: WeightGenerator|float|int=DEFAULT_EDGE_WEIGHT
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
    G = Graph(nodes=nodes)

    # Add edges
    rs = make_random_state(seed)
    edges = ((nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i+1, len(nodes)))
    for u, v in edges:
        # Skip if random uniform variable r > p
        if rs.uniform(0.0, 1.0) > p:
            continue
        # Determine weight an add edge
        weight = weights() if callable(weights) else weights
        G.add_edge(u, v, weight)

    return G
