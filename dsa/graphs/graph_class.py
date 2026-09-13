from collections import defaultdict
from typing import Hashable, Iterable, Self


class GraphError(Exception):
    pass


class Graph[N: Hashable]:
    def __init__(self, nodes: Iterable[N]=()) -> None:
        self._adj: dict[N, dict[N, float]] = {}
        self._node_attrs: dict[N, dict[str, object]] = defaultdict(dict)
        self._edge_attrs: dict[tuple[N, N], dict[str, object]] = defaultdict(dict)

    def add_node(self, node: N, **attrs: object) -> Self:
        """Adds a node to the graph. Arbitrary node attributes can be passed as keyword arguments"""

        if node in self:
            raise GraphError(f"Attempted adding node {node}, which is already added")

        self._adj[node] = {}
        if attrs:
            self._node_attrs[node].update(**attrs)
        return self

    def add_edge(self, u: N, v: N, dist: float, **attrs: object) -> Self:
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

        # Register the u -> v distance
        if u in self._adj:
            self._adj[u][v] = dist
        else:
            self._adj[u] = {v: dist}

        # Update attributes if any are passed
        if attrs:
            self._edge_attrs[key].update(**attrs)

        return self

    def has_edge(self, u: N, v: N) -> bool:
        return v in self._adj.get(u, {})

    def __contains__(self, node: N) -> bool:
        return node in self._adj