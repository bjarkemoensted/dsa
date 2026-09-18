from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, Hashable, Iterator

if TYPE_CHECKING:
    from dsa.graphs.graph_class import Graph


class ViewBase[N: Hashable](abc.ABC):
    """Base class for a view of elements of a graph for abstracting away
    stuff like edge iteration, edge counting etc. This is just to
    separate out some of the logic for e.g. iterating over edges,
    depending on directedness etc"""

    def __init__(self, G: Graph[N]) -> None:
        self.G = G

    @abc.abstractmethod
    def __iter__(self) -> Iterator[Any]:
        raise NotImplementedError

    def __len__(self) -> int:
        # Replace by something more efficient when possible
        return sum(1 for _ in self)

    def __str__(self) -> str:
        return str(list(self))


class EdgeViewBase[N](ViewBase[N]):
    pass


class EdgeView[N: Hashable](EdgeViewBase[N]):
    """View of the edges in an undirected graph."""

    def __iter__(self) -> Iterator[tuple[N, N]]:
        seen: set[N] = set()
        for u, d in self.G._adj.items():
            for v in d:
                if v not in seen:
                    yield u, v
                #
            seen.add(u)

    def __len__(self) -> int:
        n_links = 0
        n_self = 0
        for node, neighbors in self.G._adj.items():
            has_self_link = node in neighbors
            n_links += len(neighbors) - has_self_link
            n_self += has_self_link
        res = n_links // 2 + n_self
        return res


class DirectedEdgeView[N: Hashable](EdgeViewBase[N]):
    def __iter__(self) -> Iterator[tuple[N, N]]:
        yield from ((u, v) for u, d in self.G._adj.items() for v in d)

    def __len__(self) -> int:
        res = sum(len(neighbors) for neighbors in self.G._adj.values())
        return res


class NodeView[N](ViewBase[N]):
    """View of nodes in a graph"""

    def __iter__(self) -> Iterator[N]:
        yield from self.G._adj

    def __len__(self) -> int:
        return len(self.G._adj)
