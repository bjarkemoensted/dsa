from typing import Generic, TypeAlias

from dsa.data_structures.linear.base import BaseContainer, T
from dsa.data_structures.heap_operations import heappop, heappush


prioritytype: TypeAlias = float|tuple[float, int]
elemtype: TypeAlias = tuple[prioritytype, T]


def _get_priority(elem: tuple):
    priority, _ = elem
    return priority


class PriorityQueue(BaseContainer, Generic[T]):
    """Priority queue, using a min-heap under the hood (i.e. elements with lowest priorities
    are first returned from the queue)."""
    
    arr: list[elemtype]
    
    def __init__(self, maxsize = -1, stable=True) -> None:
        """maxsize (int, optional) - max allowed number of elements in the queue. -1 for unlimited size.
        stable (bool, default: True) - indicates whether the queue is stable. If stable, elements with equal
            priorities are returned in the order added."""

        super().__init__(maxsize)
        self.stable = stable
        self.arr = []
        self._counter = 0
    
    def _size(self):
        return len(self.arr)

    def _put(self, item, priority: float=0) -> None:
        priority_: prioritytype = (priority, self._counter) if self.stable else priority
        if self.stable:
            self._counter += 1

        elem: elemtype = (priority_, item)
        heappush(self.arr, elem, key=_get_priority)
    
    def _get(self) -> T:
        _, item = heappop(self.arr, key=_get_priority)
        return item
    
    def to_list(self):
        if not self.arr:
            return []
        _, res = zip(*self.arr)
        return res
    #
