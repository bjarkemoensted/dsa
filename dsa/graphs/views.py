from __future__ import annotations
import abc
from typing import Hashable, Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    from dsa.graphs.graph_class import Graph


class EdgeViewBase[N: Hashable](abc.ABC):
    """Edge view base blass - for abstracting away stuff like edge iteration,
    edge counting etc. This is just to separate out some of the logic
    for e.g. iterating over edges depending on directedness etc"""

    def __init__(self, G: Graph[N]) -> None:
        self.G = G

    @abc.abstractmethod
    def __iter__(self) -> Iterator[tuple[N, N]]:
        raise NotImplementedError

    def __len__(self) -> int:
        # TODO be more sneaky here!!!
        res = sum(1 for _ in self)
        return res

    def __str__(self) -> str:
        return str(list(self))


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


class DegreeView[N: Hashable]:
    def iterate_node_edges(
        self,
        node: N,
        incoming: bool,
        outgoing: bool,
        weighted: bool
        ) -> Iterator[tuple[N, int|float]]:

        out_edges = ((other, (node, other)) for other in self.G._succ[node])
        in_edges = ((other, (other, node)) for other in self.G._pred[node])
        generators: list[Iterator[tuple[N, tuple[N, N]]]] = []
        if outgoing:
            generators.append(out_edges)
        if incoming:
            generators.append(in_edges)

        degs: dict[N, float|int] = {}

        for g in generators:
            for other, (u, v) in g:
                weight = self.G._adj[u][v]
                w = weight if weighted else 1
                degs[other] = degs.get(other, 0) + w

        yield from degs.items()
        
    def _iter(self, node: N, weighted: bool=True) -> Iterator[tuple[N, int|float]]:
        for neighbor, weight in self.G._adj.get(node, {}).items():
            w = weight if weighted else 1
            yield neighbor, w

    def __init__(self, G: Graph[N]) -> None:
        self.G = G


