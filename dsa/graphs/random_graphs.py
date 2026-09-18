"""Tooling for initializing various random graphs"""

from typing import Callable, Iterator, Sequence

import numpy as np

from dsa.graphs.graph_class import DEFAULT_EDGE_WEIGHT, DiGraph, Graph
from dsa.utils.randomization import RandomSeeder, make_random_state, make_random_state_numpy

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
        ) -> Graph[int]:
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
        # If the graph is undirected, randomly add v->u instead of u->v to check edge logic
        if not directed and rs.uniform(0.0, 1.0) <= 0.5:
            u, v = v, u
        G.add_edge(u, v, weight)

    return G


def barabasi_albert(
        n: int,
        m: int,
        seed: RandomSeeder=None,
        weights: WeightGenerator|float|int=DEFAULT_EDGE_WEIGHT,
        ) -> Graph[int]:
    """Generates a Barabási-Albert graph, with n nodes.
    Each new node is attached to (up to) m existing ones, with probabilities that
    are propoertional to the current degree of each node (preferential attachment)."""

    # Initialize randomstate (using numpy for non-uniform probability distributions)
    rs = make_random_state_numpy(seed)
    # Initialize the graph
    nodes = list(range(n))
    G = Graph(nodes=nodes)
    # Running tally of the degree of each node, just to avoid recomputations
    p_weights_running = np.array([0.0 for _ in nodes])

    # Skip the first node because we won't have any existing nodes ot connect to
    for i in range(1, n):
        new_node = nodes[i]
        # Inclusion mask, to avoid connecting twice to the same node
        include = np.array([1.0 for _ in range(n)])

        # Choose up to m nodes to connect to
        n_choose = min(m, i)

        for _ in range(n_choose):
            # Get the probability weightings
            p = p_weights_running*include

            # If all weightings are 0, we haven't added any links yet, so just choose the first node
            if np.isclose(sum(p), 0.0):
                p[0] = 1.0

            # Normalize the probabilities
            norm_factor = 1.0/sum(p)
            p *= norm_factor

            # Choose a node according to the probabilities, and connect
            other_ind = rs.choice(n, p=p)
            weight = weights() if callable(weights) else weights
            G.add_edge(new_node, nodes[other_ind], weight=weight)
            # Exclude the newly linked node to avoid attempts to connect to it again
            include[other_ind] = 0.0
            # Update running probability weightings
            p_weights_running[i] = G.degree(nodes[i])
            p_weights_running[other_ind] = G.degree(nodes[other_ind])

    return G