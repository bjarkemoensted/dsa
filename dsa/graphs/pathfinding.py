from typing import Callable, Iterator

from dsa.data_structures.linear.priority_queue import PriorityQueue
from dsa.graphs.exceptions import NoPathError
from dsa.graphs.graph_class import Graph

# For a callable yielding the neighbors and their distances to a given node
type NeighborGetter[N] = Callable[[N], Iterator[tuple[N, int|float]]]


def _iterate_dijkstra_path_lengths[N](
        from_: N,
        neighbor_getter: NeighborGetter[N]
    ) -> Iterator[tuple[N, int|float]]:
    """Iterates over reachable nodes and their shortest distances as computed by the Dijkstra algorithm.
    from_: The node from which to start the graph traversal.
    neighbor_getter: Callable for iterating over the next nodesfrom a given node. This will typically
    be simply the successor nodes, but the predecessors can also be used to iterate over shortest paths
    to a given destination, or to modify which edges are allowed etc."""

    queue: PriorityQueue[N] = PriorityQueue()
    d0 = 0
    d_g: dict[N, int|float] = {from_: d0}  # Shortest path to every node encountered
    # Initially, only the shortest path to the source is known (distance 0)
    queue.push(item=from_, priority=d0)

    while queue:
        # Consider the currently shortest distance found to any node
        f, u = queue.pop_element()
        shortest = d_g[u]
        
        # If a shorter distance to u has been found since adding it to the queue, skip it
        if f > shortest:
            continue

        # We've found the shortest distance to the node just popped
        yield u, shortest

        for v, delta in neighbor_getter(u):            
            # Path length to v via u
            g_tentative = d_g[u] + delta
            # Put v on the queue if this path beats the current record to v
            improved = g_tentative < d_g.get(v, float("inf"))
            if improved:
                d_g[v] = g_tentative
                queue.push(item=v, priority=g_tentative)


def shortest_path_dijkstra[N](G: Graph[N], source: N, target: N) -> int|float:
    """Uses Dijkstra's algorithm to find the shortest path from source to target."""

    for node, dist in _iterate_dijkstra_path_lengths(from_=source, neighbor_getter=G.successors):
        if node == target:
            return dist
        
    raise NoPathError


def single_source_dijkstra_path_lengths[N](G: Graph[N], source: N) -> dict[N, int|float]:
    dists = _iterate_dijkstra_path_lengths(from_=source, neighbor_getter=G.successors)
    res = {target: dist for target, dist in dists}
    return res


def single_target_dijkstra_path_lengths[N](G: Graph[N], target: N) -> dict[N, int|float]:
    dists = _iterate_dijkstra_path_lengths(from_=target, neighbor_getter=G.predecessors)
    res = {target: dist for target, dist in dists}
    return res


def has_path[N](G: Graph[N], source: N, target: N) -> bool:
    """Determines whether a path from source to target exists on G.
    Works using simple breadth-first search (BFS) - starting fro mthe source node,
    it repeatedly add unvisited adjacent nodes, checking for the target node"""

    visited: set[N] = set()
    front = {source}

    while front:
        if target in front:
            return True
        # Update sets of visited and new nodes
        visited |= front
        front = {v for u in front for v, _ in G.successors(u) if v not in visited}

    return False
