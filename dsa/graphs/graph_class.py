from __future__ import annotations

from collections import defaultdict
from itertools import pairwise
from typing import Any, ClassVar, Hashable, Iterable, Iterator, Mapping, Self

import networkx as nx

from dsa.graphs import views
from dsa.graphs.exceptions import GraphError, NoPathError

type AttrType = Mapping[Any, object]

DEFAULT_EDGE_WEIGHT = 1
_NETWORKX_WEIGHT_ATTRIBUTE = "weight"


class Graph[N: Hashable]:
    """Represents a graph containing nodes-vertices, connected by links-edges.
    This class focuses on logic for adding-removing nodes and edges, and updating their attributes.
    Methods for discovering paths are defined as external functions that take a
    graph instance as one of their arguments"""

    directed: ClassVar[bool] = False
    
    def __init__(
            self,
            nodes: Iterable[N]=(),
            edges: Iterable[tuple[N, N]|tuple[N, N, int|float]]=(),
            ) -> None:
        self._adj: dict[N, dict[N, float]] = {}

        # Set of predecessor nodes for each node {v: {u1, u2, ...}} means u1 and u2 link to v
        self._pred: dict[N, set[N]] = defaultdict(set)
        
        self._node_attrs: dict[N, dict[Hashable, object]] = defaultdict(dict)
        self._edge_attrs: dict[tuple[N, N], dict[Hashable, object]] = defaultdict(dict)

        self.add_nodes_from(nodes)
        self.add_edges_from(edges)

    def add_node(self, node: N, attrs: AttrType|None=None) -> Self:
        """Adds a node to the graph. Arbitrary node attributes can be passed as keyword arguments"""

        if node in self:
            raise GraphError(f"Attempted adding node {node}, which is already added")

        self._adj[node] = {}
        if attrs:
            self._node_attrs[node].update(attrs)
        return self

    def add_nodes_from(self, nodes: Iterable[N]) -> Self:
        for node in nodes:
            self.add_node(node)
        return self

    def remove_node(self, node: N) -> Self:
        del self._adj[node]

        for other, _ in self.successors(node):
            self._remove_edge(node, other)
        for other, _ in self.predecessors(node):
            self._remove_edge(other, node)
        self._node_attrs.pop(node, None)
        return self

    def _add_edge(self, u: N, v: N, weight: float, attrs: AttrType|None=None) -> None:
        """Add a single edge u -> v
        To be called after various checks like node existance"""

        # Register the u -> v distance
        if u in self._adj:
            self._adj[u][v] = weight
        else:
            self._adj[u] = {v: weight}

        if self.directed:
            self._pred[v].add(u)

        # Update attributes if any are passed
        if attrs:
            self._edge_attrs[(u, v)].update(attrs)

    def add_edge(self, u: N, v: N, weight: int|float|None=None, attrs: AttrType|None=None) -> Self:
        """Add an edge connect node u to node v.
        dist: The distance.
        **attrs: Arbitrary attributes of the edge"""

        weight_ = 1 if weight is None else weight
        # Ensure nodes exist
        key = (u, v)
        for node in key:
            if node not in self:
                self.add_node(node)

        self._add_edge(u, v, weight=weight_, attrs=attrs)
        if not self.directed:
            self._add_edge(v, u, weight=weight_, attrs=attrs)

        return self

    def add_edges_from(self, edges: Iterable[tuple[N, N]|tuple[N, N, int|float]]) -> Self:
        """Adds multiple edges from an iterable. Each element must be either a 2-tuple (u, v),
        or a 3-tuple (u, v, weight)"""

        for edge in edges:
            if len(edge) == 2:
                u, v = edge
                self.add_edge(u, v)
            elif len(edge) == 3:
                u, v, w = edge
                self.add_edge(u, v, w)
            else:
                raise ValueError(f"Invalid edge tuple: {edge}")

        return self

    def _remove_edge(self, u: N, v: N) -> None:
        del self._adj[u][v]
        self._edge_attrs.pop((u, v), None)

    def remove_edge(self, u: N, v: N) -> Self:
        self._remove_edge(u, v)
        if not self.directed:
            self._remove_edge(v, u)
        return self
    
    def has_edge(self, u: N, v: N) -> bool:
        return v in self._adj.get(u, {})

    def __contains__(self, node: N) -> bool:
        return node in self._adj

    def edges(self) -> views.EdgeViewBase[N]:
        if self.directed:
            return views.DirectedEdgeView(self)
        else:
            return views.EdgeView(self)

    def degree(self, node: N, weighted: bool=True) -> int|float:
        weights = (w for _, w in self.successors(node))
        if weighted:
            return sum(weights)
        else:
            return sum(1 for _ in weights)

    def iter_edge_weights(self) -> Iterator[tuple[N, N, float|int]]:
        for u in self.nodes():
            yield from ((u, v, w) for v, w in self.successors(u))

    def successors(self, node: N) -> Iterator[tuple[N, int|float]]:
        yield from self._adj[node].items()

    def predecessors(self, node: N) -> Iterator[tuple[N, int|float]]:
        others = self._pred[node] if self.directed else self._adj[node]
        for pred in others:
            weight = self._adj[pred][node]
            yield pred, weight

    def neighbors(self, node: N) -> Iterator[N]:
        yield from self._adj[node]

    def nodes(self) -> views.NodeView[N]:
        return views.NodeView(self)

    def __len__(self) -> int:
        return len(self._adj)

    def to_networkx(self) -> nx.Graph[N]:
        return _as_networkx(self)

    def compute_path_length(self, path: Iterable[N]) -> int|float:
        """Takes a path, represented by an iterable of nodes..
        Returns the length of the path, raising a NoPathError if any edges in a path do not exist"""

        res: int|float = 0
        for u, v in pairwise(path):
            try:
                res += self._adj[u][v]
            except KeyError as e:
                raise NoPathError(f"Path contained missing edge: {u} -> {v}") from e

        return res

class DiGraph[N: Hashable](Graph[N]):
    directed = True


def _initialize_equivalent_networkx_class[N: Hashable](G: Graph[N]) -> nx.Graph[N]:
    """Determines the appropriate networkx graph class for a graph and instantiates it"""
    match G:
        case DiGraph():
            return nx.DiGraph()
        case Graph():
            return nx.Graph()
        case _:
            raise RuntimeError(f"Could not determine appropriate networkx type for {type(G)}")


def _as_networkx[N: Hashable](G: Graph[N]) -> nx.Graph[N]:
    """Converts a graph object into a corresponding networkx graph"""

    # Initialize the networkx graph
    res = _initialize_equivalent_networkx_class(G)

    # Add the nodes
    for node in G.nodes():
        node_attrs: dict[str, Any] = {}
        for k, v in G._node_attrs[node].items():
            if not isinstance(k, str):
                raise TypeError
            node_attrs[k] = v
        res.add_node(node, **node_attrs)

    # Add the edges
    edges = ((u, v, G._adj[u][v]) for u, v in G.edges())
    for u, v, weight in edges:
        edge_attrs: dict[str, Any] = {_NETWORKX_WEIGHT_ATTRIBUTE: weight}
        for k_, v_ in G._edge_attrs[(u, v)].items():
            if not isinstance(k_, str):
                raise TypeError
            if k_ == _NETWORKX_WEIGHT_ATTRIBUTE:
                raise ValueError(f"{_NETWORKX_WEIGHT_ATTRIBUTE!r} is reserved for weights in networkx graphs!")
            edge_attrs[k_] = v_

        res.add_edge(u, v, **edge_attrs)
        
    return res
