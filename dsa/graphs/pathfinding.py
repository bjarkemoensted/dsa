from typing import Callable, Iterator, Literal, overload

from dsa.data_structures.linear.priority_queue import PriorityQueue
from dsa.graphs.exceptions import NoPathError
from dsa.graphs.graph_class import Graph

# For a callable yielding the neighbors and their distances to a given node
type NeighborGetter[N] = Callable[[N], Iterator[tuple[N, int|float]]]


def reconstruct_path[N](camefrom: dict[N, N], target: N) -> list[N]:
    """Given a dict of predecessor nodes (so {u: v} means that we arrive to node v via node u), and a target node,
    this reconstructs the full path and returns it"""
    # Build the reverse path, starting with the final node
    path = [target]
    # Keep adding the previous node until we run out
    while path[-1] in camefrom:
        path.append(camefrom[path[-1]])
    # Reverse it in-place and return the path
    path.reverse()
    return path


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


def dijkstra_path_length[N](G: Graph[N], source: N, target: N) -> int|float:
    """Uses Dijkstra's algorithm to find the shortest path from source to target."""

    for node, dist in _iterate_dijkstra_path_lengths(from_=source, neighbor_getter=G.successors):
        if node == target:
            return dist
        
    raise NoPathError


def dijkstra_path[N](G: Graph[N], source: N, target: N) -> list[N]:
    
    queue: PriorityQueue[N] = PriorityQueue()
    d0 = 0
    d_g: dict[N, int|float] = {source: d0}  # Shortest path to every node encountered
    # Initially, only the shortest path to the source is known (distance 0)
    queue.push(item=source, priority=d0)
    camefrom: dict[N, N] = {}

    while queue:
        # Consider the currently shortest distance found to any node
        f, u = queue.pop_element()
        shortest = d_g[u]
        
        # If a shorter distance to u has been found since adding it to the queue, skip it
        if f > shortest:
            continue

        # We're done if we pop the target node
        if u == target:
            return reconstruct_path(camefrom=camefrom, target=target)

        for v, delta in G.successors(u):            
            # Path length to v via u
            g_tentative = d_g[u] + delta
            # Put v on the queue if this path beats the current record to v
            improved = g_tentative < d_g.get(v, float("inf"))
            if improved:
                d_g[v] = g_tentative
                queue.push(item=v, priority=g_tentative)
                camefrom[v] = u

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


@overload
def a_star[N](
        G: Graph[N],
        source: N,
        target: N,
        heuristic: Callable[[N], int|float],
        return_path: bool=True
        ) -> list[N]: ...
@overload
def a_star[N](
        G: Graph[N],
        source: N,
        target: N,
        heuristic: Callable[[N], int|float],
        return_path: Literal[False]=...
        ) -> int|float: ...
def a_star[N](
        G: Graph[N],
        source: N,
        target: N,
        heuristic: Callable[[N], int|float],
        return_path: bool=True
        ) -> list[N]|int|float:
    """A* algorithm for shortest path from a single source to a single target.
    Accepts a heuristic callable which must take a single node, and return a lower
    bound on the distance from that node to the target. For example, if the nodes on the
    graph are located on a plane, the euclidean distance can be used.
    It works similarly to Dijkstra, except the priority queue containing the nodes works
    slightly differently. In Dijkstra, the queue is keyed by the distance g to the nodes.
    In A*, a heuristic function is used to provide a lower bound h on the remaining part of the path,
    and the queue is then keyed by the lower bound f = g + h on a path through each node.
    This ensures that when the target node is popped from the heap, a shortest path has been found,
    as any path which remains to be found will have at least the same distance.
    A* reduces to Dijkstra's algorithm if the heuristic function returns 0 for all nodes.
    return_path can be set to False to return only the path length."""

    # Note the current shortest distance found to any other node
    g0 = 0
    d_g: dict[N, int|float] = {source: g0}

    # Add the source node to the priority queue, keyed by its lower bound
    h0 = heuristic(source)
    f0 = g0 + h0
    queue: PriorityQueue[N] = PriorityQueue()
    queue.push(source, priority=f0)

    # Keep track of how we got to each node, for path reconstruction
    camefrom: dict[N, N] = {}

    while queue:
        u = queue.pop()

        # If we find the target, return the path/length
        if u == target:
            if return_path:
                return reconstruct_path(camefrom, target)
            else:
                return d_g[u]

        # Look at the neighbors of u
        for v, delta in G.successors(u):
            g = d_g[u] + delta
            improved = g < d_g.get(v, float("inf"))
            if improved:
                d_g[v] = g
                h = heuristic(v)
                f = g + h
                queue.push(v, priority=f)
                camefrom[v] = u

    raise NoPathError


def single_source_bellman_ford_paths[N](G: Graph[N], source: N) -> tuple[dict[N, N], dict[N, int|float]]:
    """Determine all shortest paths from a given source node, using the Bellman-Ford algorithm.
    Returns a tuple of
    1) The predecessors dict, and
    2) Shortest distance dict (target node as key and path kength as value)"""

    camefrom: dict[N, N] = {}
    dists: dict[N, int|float] = {source: 0}

    for _ in range(len(G.nodes())):
        for u, v, delta in G.iter_edge_weights():
            d_tentative = dists.get(u, float("inf")) + delta
            improved = d_tentative < dists.get(v, float("inf"))
            if improved:
                dists[v] = d_tentative
                camefrom[v] = u
            #
        #
    
    # TODO: CHECK NEGATIVE CYCLES!!!
    return camefrom, dists


# TODO There's a lot of boilerplate in keeping predecessors (camefrom) and dists updated, and
# Using various algorithms to construct single-source/single-target path lengths + paths.
# Consider having a class which is initialized with the graph and a source/target node.
# Then we can abstract away the iteration (like _iterate_dijkstra_path_lengths does currently),
# Store predecessor + dist dicts at the class, and use class methods like .path, .dist .all_dists, all_paths
# to compute the different quantities.
def bellman_ford_path[N](G: Graph[N], source: N, target: N) -> list[N]:
    """Uses the Bellman-Ford algorithm to determine the shortest path from source to target node"""
    camefrom, dists = single_source_bellman_ford_paths(G, source)

    if target not in dists:
        raise NoPathError

    return reconstruct_path(camefrom, target=target)


def floyd_warshall[N](G: Graph[N]) -> dict[N, dict[N, float|int]]:
    """TODO copied from old coursework. Go over!!!"""
    import math

    import numpy as np
    # Initialize solution matrix
    node_list = list(G.nodes())
    rev = {node: i for i, node in enumerate(node_list)}
    n = len(G.nodes())
    A = np.ndarray(shape = (n,n,n+1))
    A.fill(float('inf'))
    
    # set up base cases
    for (u, v, w) in G.iter_edge_weights():
        A[rev[u], rev[v], 0] = w
    
    for i in range(n):
        A[i,i,0] = 0
    
    count = 0
    for k in range(1, n+1):
        for i in range(n):
            for j in range(n):
                case1 = A[i,j,k-1]  # If k isn't in the path
                case2 = A[i,k-1,k-1] + A[k-1,j,k-1]  #If k gets plucked
                
                A[i,j,k] = min(case1, case2)
                count += 1
            #
        #
    #
    
    shortest = float('inf')
    for i in range(n):
        for j in range(n):
            val = A[i,j,n]
            if i == j and val < 0:
                raise RuntimeError("Negative cycle")
            if val < shortest:
                shortest = val
            #
        #
    
    best = A[:, :, n]
    res = {
        node_list[ui]:
            {node_list[vi]: round(w) for vi, w in enumerate(row) if not math.isinf(w)}
            for ui, row in enumerate(best)
        }
    return res