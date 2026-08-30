"""Implements simple linear data structures (stacks, queues)"""

from typing import cast

from dsa.data_structures.linear.base import DEFAULT_ARR_SIZE, BaseContainer


class Queue[T](BaseContainer):
    """Queue data structure. Implementation follows CLRS section 10.1.
    The invariants here are the pointers .tail and .head which refer to
    the next free slot, and the most recently inserted element, respectively (except when the
    queue is empty)."""

    arr: list[T|None]

    def __init__(self, maxsize: int=-1):
        super().__init__(maxsize=maxsize)
        
        initial_size = maxsize + 1 if maxsize != -1 else DEFAULT_ARR_SIZE
        self.arr = [None for _ in range(initial_size)]
        self.head = 0
        self.tail = 0

    def _size(self) -> int:
        return (self.tail - self.head) % len(self.arr)
    
    def _grow_array(self) -> None:
        inds = ((self.head + i) % len(self.arr) for i in range(self.size()))
        vals = [self.arr[i] for i in inds]
        self.arr = [None for _ in range(2*self.size())]
        for i, val in enumerate(vals):
            self.arr[i] = val
    
    def _put(self, item: T) -> None:
        at_capacity = self.size() == len(self.arr) - 1
        if at_capacity:
            self._grow_array()
        
        self.arr[self.tail] = item
        self.tail = (self.tail + 1) % len(self.arr)
    
    def _get(self) -> T:
        elem = self.arr[self.head]
        self.head = (self.head + 1) % len(self.arr)
        
        return cast(T, elem)
    
    def to_list(self) -> list[T]:
        inds = ((self.head + i) % len(self.arr) for i in range(self.size()))
        res = [self.arr[i] for i in inds]
        return cast(list[T], res)

    def enqueue(self, item: T) -> None:
        self.put(item)
    
    def dequeue(self) -> T:
        return self.get()
