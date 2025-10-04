"""Implements simple linear data structures (stacks, queues)"""

from abc import ABC, abstractmethod
from typing import (
    cast,
    Generic,
    TypeVar
)

from dsa.data_structures.heap_operations import heappush, heappop

T = TypeVar('T')  # exposed type

DEFAULT_ARR_SIZE = 8


class BaseContainer(ABC, Generic[T]):
    
    def __init__(self, maxsize: int=-1):
        self.maxsize = maxsize
    
    def size(self):
        return self._size()
    
    def empty(self) -> bool:
        """Whether the data structure is currently empty"""
        res = self.size() == 0
        return res
    
    def full(self) -> bool:
        """Whether the data structure is currently full"""
        return self.size() == self.maxsize
    
    def get(self) -> T:
        if self.empty():
            raise RuntimeError(f"{self.__class__.__name__} is empty")
        return self._get()
    
    def put(self, item: T, **kwargs) -> None:
        if self.full():
            raise RuntimeError(f"{self.__class__.__name__} is full, can't add item ({item})")
        
        return self._put(item, **kwargs)
    
    @abstractmethod
    def _get(self) -> T:
        raise NotImplementedError
    
    @abstractmethod
    def _put(self, item: T, **kwargs) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def _size(self) -> int:
        raise NotImplementedError
    
    @abstractmethod
    def to_list(self) -> list[T]:
        raise NotImplementedError
    #


class Queue(BaseContainer, Generic[T]):
    """Queue data structure. Implementation follows CLRS section 10.1.
    The invariants here are the pointers .tail and .head which refer to
    the next free slot, and the most recently inserted element, respectively (except when the
    queue is empty)."""
    
    def __init__(self, maxsize: int=-1):
        super().__init__(maxsize=maxsize)
        
        initial_size = maxsize + 1 if maxsize != -1 else DEFAULT_ARR_SIZE
        self.arr = [None for _ in range(initial_size)]
        self.head = 0
        self.tail = 0

    def _size(self):
        return (self.tail - self.head) % len(self.arr)
    
    def _grow_array(self):
        inds = ((self.head + i) % len(self.arr) for i in range(self.size()))
        vals = [self.arr[i] for i in inds]
        self.arr = [None for _ in range(2*self.size())]
        for i, val in enumerate(vals):
            self.arr[i] = val
        #
    
    def _put(self, item):
        at_capacity = self.size() == len(self.arr) - 1
        if at_capacity:
            self._grow_array()
        
        self.arr[self.tail] = item
        self.tail = (self.tail + 1) % len(self.arr)
    
    def _get(self):
        elem = self.arr[self.head]
        self.head = (self.head + 1) % len(self.arr)
        
        return cast(T, elem)
    
    def to_list(self) -> list[T]:
        inds = ((self.head + i) % len(self.arr) for i in range(self.size()))
        res = [self.arr[i] for i in inds]
        return cast(list[T], res)
    #

    def enqueue(self, item: T):
        self.put(item)
    
    def dequeue(self):
        return self.get()
    #


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
