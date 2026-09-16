from __future__ import annotations

from collections import defaultdict
from typing import Any, ClassVar, Hashable, Iterable, Iterator, Mapping, Self

import networkx as nx

from dsa.graphs.exceptions import GraphError

type AttrType = Mapping[Any, object]

DEFAULT_EDGE_WEIGHT = 1
_NETWORKX_WEIGHT_ATTRIBUTE = "weight"


class EdgeView[N: Hashable]:
    """TODO docs"""
    
    def __init__(self, G: Graph[N]) -> None:
        self._G = G

    def _iter_directed(self) -> Iterator[tuple[N, N]]:
        yield from ((u, v) for u, d in self._G._adj.items() for v in d)

    def _iter_undirected(self) -> Iterator[tuple[N, N]]:
        seen: set[N] = set()
        for u, d in self._G._adj.items():
            for v in d:
                if v not in seen:
                    yield u, v
                #
            seen.add(u)

    def __iter__(self) -> Iterator[tuple[N, N]]:
        iterator_ = self._iter_directed if self._G.directed else self._iter_undirected
        yield from iterator_()


class Graph[N: Hashable]:
    """TODO docs"""

    directed: ClassVar[bool] = False
    
    def __init__(self, nodes: Iterable[N]=()) -> None:
        self._adj: dict[N, dict[N, float]] = {}

        self._pred: dict[N, set[N]] = defaultdict(set)
        self._succ: dict[N, set[N]] = defaultdict(set)
        
        self._node_attrs: dict[N, dict[Hashable, object]] = defaultdict(dict)
        self._edge_attrs: dict[tuple[N, N], dict[Hashable, object]] = defaultdict(dict)

        for node in nodes:
            self.add_node(node)

    def add_node(self, node: N, attrs: AttrType|None=None) -> Self:
        """Adds a node to the graph. Arbitrary node attributes can be passed as keyword arguments"""

        if node in self:
            raise GraphError(f"Attempted adding node {node}, which is already added")

        self._adj[node] = {}
        if attrs:
            self._node_attrs[node].update(attrs)
        return self

    def remove_node(self, node: N) -> Self:
        del self._adj[node]

        for other in self._succ.pop(node, ()):
            self._remove_edge(node, other)
        for other in self._pred.pop(node, ()):
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

        self._succ[u].add(v)

        if self.directed:
            self._pred[v].add(u)

        # Update attributes if any are passed
        if attrs:
            self._edge_attrs[(u, v)].update(attrs)

    def add_edge(self, u: N, v: N, weight: float, attrs: AttrType|None=None) -> Self:
        """Add an edge connect node u to node v.
        dist: The distance.
        **attrs: Arbitrary attributes of the edge"""

        # Ensure nodes exist
        key = (u, v)
        for node in key:
            if node not in self:
                self.add_node(node)

        self._add_edge(u, v, weight=weight, attrs=attrs)
        if not self.directed:
            self._add_edge(v, u, weight=weight, attrs=attrs)

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

    def edges(self) -> EdgeView[N]:
        return EdgeView(self)

    def iter_edge_weights(self) -> Iterator[tuple[N, N, float|int]]:
        for u, v in self.edges():
            w = self._adj[u][v]
            yield u, v, w

    def neighbors_with_weights(self, node: N) -> Iterator[tuple[N, float|int]]:
        yield from (self._adj[node].items())

    def neighbors(self, node: N) -> Iterator[N]:
        yield from (v for v, _ in self.neighbors_with_weights(node))

    def nodes(self) -> Iterator[N]:
        yield from self._adj

    def to_networkx(self) -> nx.Graph[N]:
        return _as_networkx(self)


def _initialize_equivalent_networkx_class[N: Hashable](G: Graph[N]) -> nx.Graph[N]:
    match G:
        case Graph():
            return nx.Graph()
        case _:
            raise RuntimeError(f"Could not determine appropriate networkx type for {type(G)}")


def _as_networkx[N: Hashable](G: Graph[N]) -> nx.Graph[N]:
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
    for u, v, weight in G.iter_edge_weights():
        edge_attrs: dict[str, Any] = {_NETWORKX_WEIGHT_ATTRIBUTE: weight}
        for k_, v_ in G._edge_attrs[(u, v)].items():
            if not isinstance(k_, str):
                raise TypeError
            if k_ == _NETWORKX_WEIGHT_ATTRIBUTE:
                raise ValueError(f"{_NETWORKX_WEIGHT_ATTRIBUTE!r} is reserved for weights in networkx graphs!")
            edge_attrs[k_] = v_

        res.add_edge(u, v, **edge_attrs)
        
    return res
