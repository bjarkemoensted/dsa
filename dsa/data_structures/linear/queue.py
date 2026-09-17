"""Implements simple linear data structures (stacks, queues)"""

from typing import Iterator

from dsa.data_structures.linear.base import DEFAULT_ARR_SIZE, BaseContainer, Sentinel

NOT_SET = Sentinel()


class Queue[T](BaseContainer[T]):
    """Queue data structure. Implementation follows CLRS section 10.1.
    The invariants here are the pointers .tail and .head which refer to
    the next free slot, and the most recently inserted element, respectively (except when the
    queue is empty)."""

    arr: list[T|Sentinel]

    def __init__(self, maxsize: int=-1):
        super().__init__(maxsize=maxsize)
        
        initial_size = maxsize + 1 if maxsize != -1 else DEFAULT_ARR_SIZE
        self.arr = [NOT_SET for _ in range(initial_size)]
        self.head = 0
        self.tail = 0

    def size(self) -> int:
        return (self.tail - self.head) % len(self.arr)

    def __iter__(self) -> Iterator[T]:
        inds = ((self.head + i) % len(self.arr) for i in range(self.size()))

        for i in inds:
            elem = self.arr[i]
            if isinstance(elem, Sentinel):
                raise RuntimeError
            yield elem
    
    def _grow_array(self) -> None:
        inds = ((self.head + i) % len(self.arr) for i in range(self.size()))
        vals = [self.arr[i] for i in inds]
        self.arr = [NOT_SET for _ in range(2*self.size())]
        for i, val in enumerate(vals):
            self.arr[i] = val
    
    def enqueue(self, item: T) -> None:
        """Adds an item to the tail (back) of the queue"""
        self._pre_put(item)
        at_capacity = self.size() == len(self.arr) - 1
        if at_capacity:
            self._grow_array()
        
        self.arr[self.tail] = item
        self.tail = (self.tail + 1) % len(self.arr)

    def dequeue(self) -> T:
        """Retrieves the element at the head (front) of the queue"""
        self._pre_get()
        elem = self.arr[self.head]
        if isinstance(elem, Sentinel):
            raise RuntimeError("Dequeuing an element which hasn't been set")
        self.head = (self.head + 1) % len(self.arr)
        
        return elem
