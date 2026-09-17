from dsa.data_structures.linear.priority_queue import PriorityQueue
from dsa.graphs.exceptions import NoPathError
from dsa.graphs.graph_class import Graph


def shortest_path_dijkstra[N](G: Graph[N], source: N, target: N) -> int|float:
    """Uses Dijkstra's algorithm to find the shortest path from source to target."""

    queue: PriorityQueue[N] = PriorityQueue()
    d0 = 0
    d_g: dict[N, int|float] = {source: d0}  # Shortest path to every node encountered
    # Initially, only the shortest path to the source is known (distance 0)
    queue.push(item=source, priority=d0)

    while queue:
        # Consider the currently shortest distance found to any node
        f, u = queue.pop_element()
        # If that's the target, we're done
        if u == target:
            return d_g[u]

        # If a shorter distance to u has been found since adding it to the queue, skip it
        if f > d_g[u]:
            continue

        for v, delta in G.neighbors_with_weights(u):            
            # Path length to v via u
            g_tentative = d_g[u] + delta
            # Put v on the queue if this path beats the current record to v
            improved = g_tentative < d_g.get(v, float("inf"))
            if improved:
                d_g[v] = g_tentative
                queue.push(item=v, priority=g_tentative)

    raise NoPathError


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
