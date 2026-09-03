"""A heap implementation where the heap is implemented in a class of its own.
This is a bit more cumbersome in some regards, but also has advantages. For example, options such as min vs max heap,
and choice of a key function, are only passed once, when initializing a heap instance.
This reduces the risk of forgetting to pass one or the other when e.g. pushing or popping elements,
which can lead to violations of the heap property."""

from __future__ import annotations

import math
from collections.abc import Iterable
from typing import overload

from dsa.data_structures import heap_operations
from dsa.utils.types import Comparable, Comparison, Conversion


class Heap[T]:
    """Implements a Heap class. The class supports both min- and max-heaps, and accepts an arbitrary key function,
    maintaining the heap invariant on the result of applying the function to elements on the heap.
    In other words, a standard min-heap will maintain the invariant parent <= child for all parent-child pairs,
    but if a key function f is provided, the invariant will instead be f(parent) <= f(child)."""
    
    A: list[T]
    constraint: Comparison[T]

    @overload
    def __new__[C: Comparable](cls, values: Iterable[C], min_heap: bool = ..., key: None = ...) -> Heap[C]: ...
    @overload
    def __new__[C](cls, values: Iterable[T], min_heap: bool, key: Conversion[T, C]) -> Heap[T]: ...
    @overload
    def __new__[C](cls, values: Iterable[T], min_heap: bool = ..., *, key: Conversion[T, C]) -> Heap[T]: ...
    def __new__[C](
            cls,
            values: Iterable|None=None,
            min_heap: bool=heap_operations.MIN_HEAP_DEFAULT,
            key: Conversion[T, C]|None=None
        ) -> Heap:
        return super().__new__(cls)

    def __init__[C](
            self,
            values: Iterable[T]|None=None,
            min_heap: bool=heap_operations.MIN_HEAP_DEFAULT,
            key: Conversion[T, C]|None=None
        ) -> None:
        """values: optional iterable of elements with which to initialize the heap.
        min_: Whether to use a min-heap (defaults to True).
        key: Optional callable to apply to elements before comparing (for basing the heap structure
            on some function of its elements)"""
        
        self.A = [v for v in values] if values is not None else []
        self.min_heap = min_heap
        self.key = key

        self.constraint = heap_operations.make_constraint(min_heap=self.min_heap, key=self.key)
        self.heapify()
    
    def _invariant_satisfied(self) -> bool:
        """Whether the heap satisfies the heap property"""
        return heap_operations._satisfies_heap_property(self.A, self.constraint)
    
    def heapify(self) -> None:
        """Turn the values into a heap"""

        return heap_operations._heapify(self.A, self.constraint)
    
    def push(self, item: T) -> None:
        """Pushes an element onto the heap"""

        return heap_operations._heappush(self.A, item, self.constraint)
    
    def pop(self) -> T:
        """Pops an element from the heap"""

        res = heap_operations._heappop(self.A, self.constraint)
        return res
        
    def __len__(self) -> int:
        return len(self.A)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.A})"
    
    def __str__(self) -> str:
        return repr(self)
    
    @property
    def height(self) -> int:
        """The height of the heap"""
        n_elems = len(self)
        res = math.floor(math.log2(len(self))) + 1 if n_elems > 0 else 0
        return res
    
    def ascii_tree(self) -> str:
        res = heap_operations._represent_binary_tree_as_ascii(self.A)
        return res
        