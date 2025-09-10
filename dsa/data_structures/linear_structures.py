"""Implements simple linear data structures (stacks, queues)"""

import abc
from typing import Any, cast, Generic, Iterator, Optional, TypeVar


T = TypeVar('T', bound=Any)

DEFAULT_ARR_SIZE = 8


class LinearBase(abc.ABC, Generic[T]):
    """Base class for stacks and queues. Contains some more general methods
    for e.g. checking if the data structure is full or empty, and for representing
    it as a string."""
    
    arr: list[Optional[T]]
    maxsize: int
    
    @abc.abstractmethod
    def size(self) -> int:
        raise NotImplementedError
    
    @abc.abstractmethod
    def _grow_array(self) -> None:
        """For increasing the underlying array when necessary"""
        raise NotImplementedError

    def empty(self) -> bool:
        """Whether the data structure is currently empty"""
        res = self.size() == 0
        return res
    
    def full(self) -> bool:
        """Whether the data structure is currently full"""
        if self.maxsize == -1:
            return False
        else:
            return self.size() == self.maxsize
        #
    
    @abc.abstractmethod
    def iter_inds(self) -> Iterator[int]:
        """Iterates over the indices in the array representing values stored in the data structure"""
        raise NotImplementedError
    
    def to_list(self) -> list[T]:
        res = [self.arr[i] for i in self.iter_inds()]
        return cast(list[T], res)
    
    def _symbols(self) -> tuple[tuple[int, str], ...]:
        """For representing the array of data, along with symbols indicating
        various indices (like the top of a stack, or head/tail of a queue).
        For example, we might want to represent a stack with 4 elements in its array, and
        the top currently at index i=2 as something like
            [3, 1, 3 <TOP>, 7]
        
        This method should return a tuple of tuples (i, c), where c is a symbol,
        and i is the index at which the symbol should be indicated.
        For example, this could be (2, "T") in the example above."""
        
        return ()
    
    def _repr_elem(self, i) -> str:
        """String representation of the element at index i, along with symbols
        indicating relevant indices."""
        
        s = str(self.arr[i])

        syms = [c for ii, c in self._symbols() if ii == i]
        if syms:
            s += f" <{''.join(syms)}>"
        
        return s
        
    def __str__(self):
        res = f"{self.__class__.__name__}: [{', '.join(self._repr_elem(i) for i in range(len(self.arr)))}]"
        return res
    
    def __repr__(self):
        return f"{self.__class__.__name__} (size={self.size()})"


class Stack(LinearBase, Generic[T]):
    """Stack data structure. Implementation follows CLRS section 10.1.
    An invariant here is a .top pointer which points to the most recently inserted element.
    This implementation uses zero indexing, so the top pointer is initialized at -1 rather than 0."""
    
    arr: list[Optional[T]]
    
    def __init__(self, maxsize: int=-1):
        self.maxsize = maxsize
        initial_size = maxsize if maxsize != -1 else DEFAULT_ARR_SIZE
        self.arr = [None for _ in range(initial_size)]
        self.top = -1
    
    def size(self):
        return self.top + 1
    
    def iter_inds(self):
        yield from (i for i in range(self.top + 1))
    
    def _grow_array(self):
        new_vals = (None for _ in range(len(self.arr)))
        self.arr.extend(new_vals)
        
    def pop(self) -> T:
        """Pops a single element from the stack"""
        if self.empty():
            raise RuntimeError("Can't pop from empty list")
        
        self.top -= 1
        res = self.arr[self.top + 1]
        return cast(T, res)
    
    def _symbols(self):
        res = ((self.top, "T"),)
        return res
    
    def _symbols_at_index(self, ind):
        if ind == self.top:
            return "T"
        #
    
    def push(self, elem: T) -> None:
        """Pushes a single element onto the stack"""
        
        # Throw an error if stack is full
        if self.full():
            raise RuntimeError(f"{self.__class__.__name__} is full")
        
        # Grow the underlying array if we're out of space
        at_capacity = self.size() == len(self.arr)
        if at_capacity:
            self._grow_array()
        
        # increment pointer and add to the array
        self.top += 1
        self.arr[self.top] = elem
    #


class Queue(LinearBase, Generic[T]):
    """Queue data structure. Implementation follows CLRS section 10.1.
    The invariants here are the pointers .tail and .head which refer to
    the next free slot, and the most recently inserted element, respectively (except when the
    queue is empty)."""
    
    def __init__(self, maxsize: int=-1):
        self.maxsize = maxsize
        initial_size = maxsize + 1 if maxsize != -1 else DEFAULT_ARR_SIZE
        self.arr = [None for _ in range(initial_size)]
        self.head = 0
        self.tail = 0
    
    def size(self):
        res = (self.tail - self.head) % len(self.arr)
        
        return res
    
    def iter_inds(self):
        inds = ((self.head + i) % len(self.arr) for i in range(self.size()))
        yield from inds
    
    def full(self):
        return super().full()
    
    def _increment_pointer(self, ind: int) -> int:
        new_ind = ind + 1
        if new_ind >= len(self.arr):
            return 0
        else:
            return new_ind
    
    def _grow_array(self):
        inds = ((self.head + i) % len(self.arr) for i in range(self.size()))
        vals = [self.arr[i] for i in inds]
        self.arr = [None for _ in range(2*self.size())]
        for i, val in enumerate(vals):
            self.arr[i] = val
    
    def _symbols(self):
        res = (
            (self.tail, "T"),
            (self.head, "H")
        )
        return res
    
    def enqueue(self, elem: T) -> None:
        if self.full():
            raise RuntimeError(f"{self.__class__.__name__} is full")
        
        at_capacity = self.size() == len(self.arr) - 1
        if at_capacity:
            self._grow_array()
        
        self.arr[self.tail] = elem
        self.tail = self._increment_pointer(self.tail)
    
    def dequeue(self) -> T:
        if self.empty():
            raise RuntimeError
        
        elem = self.arr[self.head]
        self.head = self._increment_pointer(self.head)
        
        return cast(T, elem)
        
    #
