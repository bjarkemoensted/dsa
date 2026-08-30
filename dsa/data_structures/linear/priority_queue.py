from dsa.data_structures.heap_operations import heappop, heappush
from dsa.data_structures.linear.base import BaseContainer

type PriorityType = float|tuple[float, int]


def _get_priority[T](elem: tuple[T, object]) -> T:
    priority, _ = elem
    return priority


class PriorityQueue[T](BaseContainer):
    """Priority queue, using a min-heap under the hood (i.e. elements with lowest priorities
    are first returned from the queue)."""
    
    arr: list[tuple[PriorityType, T]]
    
    def __init__(self, maxsize: int = -1, stable: bool=True) -> None:
        """maxsize (int, optional) - max allowed number of elements in the queue. -1 for unlimited size.
        stable (bool, default: True) - indicates whether the queue is stable. If stable, elements with equal
            priorities are returned in the order added."""

        super().__init__(maxsize)
        self.stable = stable
        self.arr: list[tuple[PriorityType, T]] = []
        self._counter = 0
    
    def _size(self) -> int:
        return len(self.arr)

    def _put(self, item: T, priority: float=0) -> None:
        priority_: PriorityType = (priority, self._counter) if self.stable else priority
        if self.stable:
            self._counter += 1

        elem: tuple[PriorityType, T] = (priority_, item)
        heappush(self.arr, elem, key=_get_priority)
    
    def _get(self) -> T:
        _, item = heappop(self.arr, key=_get_priority)
        return item
    
    def to_list(self) -> list[T]:
        res = [val for _, val in self.arr]
        return res
