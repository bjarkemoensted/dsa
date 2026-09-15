from collections import defaultdict
from typing import ClassVar, Hashable, Iterable, Iterator, Self

import networkx as nx


class GraphError(Exception):
    pass


class Graph[N: Hashable]:
    directed: ClassVar[bool] = False
    
    def __init__(self, nodes: Iterable[N]=()) -> None:
        self._adj: dict[N, dict[N, float]] = {}

        self._pred: dict[N, set[N]] = defaultdict(set)
        self._succ: dict[N, set[N]] = defaultdict(set)
        
        self._node_attrs: dict[N, dict[Hashable, object]] = defaultdict(dict)
        self._edge_attrs: dict[tuple[N, N], dict[Hashable, object]] = defaultdict(dict)

        for node in nodes:
            self.add_node(node)

    def add_node(self, node: N, attrs: dict[Hashable, object]|None=None) -> Self:
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

    def _add_edge(self, u: N, v: N, weight: float, attrs: dict[Hashable, object]|None=None) -> None:
        """Add a single edge u -> v
        To be called after various checks like node existance"""

        # Register the u -> v distance
        if u in self._adj:
            self._adj[u][v] = weight
        else:
            self._adj[u] = {v: weight}

        self._succ[u].add(v)
        self._pred[v].add(u)

        # Update attributes if any are passed
        if attrs:
            self._edge_attrs[(u, v)].update(attrs)

    def add_edge(self, u: N, v: N, weight: float, attrs: dict[Hashable, object]|None=None) -> Self:
        """Add an edge connect node u to node v.
        dist: The distance.
        **attrs: Arbitrary attributes of the edge"""

        # Raise an error if the edge already exists
        if self.has_edge(u, v):
            raise GraphError(f"Attempted to add edge {u} -> {v}, which already exists")

        # Ensure nodes exist
        key = (u, v)
        for node in key:
            if node not in self:
                self.add_node(node)

        self._add_edge(u, v, weight=weight, attrs=attrs)

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

    def edges(self) -> Iterator[tuple[N, N]]:
        yield from ((u, v) for u, d in self._adj.items() for v in d)

    def nodes(self) -> Iterator[N]:
        yield from self._adj
    #


def _initialize_new(G: nx.Graph) -> Graph:
    # TODO what's wrong with this??? !!!
    # match G:
    #     case nx.DiGraph:
    #         raise NotImplementedError
    #     case nx.Graph:
    #         return Graph()
    #     case _:
    #         raise TypeError(f"No equivalent for graph type {type(G)}")

    match type(G):
        case nx.Graph:
            return Graph()
        case _:
            raise TypeError(f"No equivalent for graph type {type(G)}")


def clone_networkx_graph[N](G: nx.Graph[N]) -> Graph[N]:
    res = _initialize_new(G)

    # TODO handle node attributes
    for node in G.nodes():
        res.add_node(node)

    for u, v, data in G.edges(data=True):
        d: dict[Hashable, object] = {k: v for k, v in data.items()}
        weight = d.pop("weight", 1)
        if not isinstance(weight, float|int):
            raise TypeError
        res.add_edge(u, v, weight=weight, attrs=d)
    
    return res