from typing import Generic

from dsa.data_structures.linear.base import BaseContainer, T
from dsa.data_structures.heap_operations import heappop, heappush


def _get_priority(elem: tuple):
    priority, _ = elem
    return priority


class PriorityQueue(BaseContainer, Generic[T]):
    def __init__(self, maxsize = -1, stable=True):
        super().__init__(maxsize)
        self.stable = stable
        self.arr = []
        self._counter = 0
    
    def _size(self):
        return len(self.arr)
    
    def _put(self, item, priority=0):
        if self.stable:
            priority = (priority, self._counter)
            self._counter += 1
        
        elem = (priority, item)
        heappush(self.arr, elem, key=_get_priority)
    
    def _get(self):
        _, item = heappop(self.arr, key=_get_priority)
        return item
    
    def to_list(self):
        if not self.arr:
            return []
        _, res = zip(*self.arr)
        return res
    #
