"""A heap implementation where the heap is implemented in a class of its own.
This is a bit more cumbersome in some regards, but also has advantages. For example, options such as min vs max heap,
and choice of a key function, are only passed once, when initializing a heap instance. This reduces the risk of forgetting
to pass one or the other when e.g. pushing or popping elements, which can lead to violations of the heap property."""

import math
from typing import (
    Callable,
    Generic,
    Iterable,
    overload,
    TypeVar
)

from dsa.data_structures.heap_operations import (
    Comparable,
    _represent_binary_tree_as_ascii,
    iterate_parent_child_pairs
)


T = TypeVar("T")
C = TypeVar("C", bound=Comparable)


def _le(a: C, b: C) -> bool:
    return a <= b


def _ge(a: C, b: C) -> bool:
    return a >= b


@overload
def _make_comparison_func(min_: bool = True, key: None = None) -> Callable[[C, C], bool]: ...
@overload
def _make_comparison_func(min_: bool = True, key: Callable[[T], C] | None = ...) -> Callable[[T, T], bool]: ...

def _make_comparison_func(min_: bool=True, key: Callable|None=None):
    """Creates a function for comparing two elements. Defaults to a function which returns a <= b,
    suitable as a comparison function for a min-heap.
    min_ can be set to False to create a function returning a >= b instead, suitable for a max-heap.
    key can be a callable which, if provided, is applied to the elements before the comparison is computed."""
    
    relation = _le if min_ else _ge
    
    def inner(a, b) -> bool:
        if key is None:
            return relation(a, b)
        else:
            return relation(key(a), key(b))
        #
    
    return inner


class Heap(Generic[T]):
    """Implements a Heap class. The class supports both min- and max-heaps, and accepts an arbitrary key function, maintaining
    the heap invariant on the result of applying the function to elements on the heap.
    In other words, a standard min-heap will maintain the invariant parent <= child for all parent-child pairs, but if a key function f
    is provided, the invariant will instead be f(parent) <= f(child)."""
    
    A: list[T]
    
    def __init__(self, values: Iterable[T]|None=None, min_: bool=True, key=None):
        """values: optional iterable of elements with which to initialize the heap.
        min_: Whether to use a min-heap (defaults to True).
        key: Optional callable to apply to elements before comparing (for basing the heap structure
            on some function of its elements)"""
        
        self.A = [v for v in values] if values is not None else []
        self.min_heap = min_
        self.key = key
        self.comp = _make_comparison_func(min_=min_, key=key)
        self._heapify()
    
    def _satisfies_heap_invariant(self) -> bool:
        """Whether the heap satisfies the heap property"""
        if not self.A:
            return True
        
        inds = iterate_parent_child_pairs(len(self.A))
        res = all(self.comp(self.A[i_parent], self.A[i_child]) for i_parent, i_child in inds)
        
        return res
    
    def _restore_down(self, i: int, stopat: int=-1) -> None:
        """Assumes all child nodes under i are heaps.
        Restores the heap at node i by repeatedly trickling values down to the 'best' child
        (i.e. the child with e.g. the lowest value in a min-heap),
        until reaching a leaf node or the index provided as stopat."""
        
        # Default to considering all nodes
        if stopat == -1:
            stopat = len(self.A)
        
        # Iterate down through the child nodes
        while (left := (i << 1) + 1) < stopat:
            # Determine the 'best' child (according to the comparison function)
            best = i
            if self.comp(self.A[left], self.A[best]):
                best = left
            
            right = left + 1
            if right < stopat and self.comp(self.A[right], self.A[best]):
                best = right
            
            if best == i:
                # If no child is better than the current node, the heap property has been restored
                return
            else:
                # Otherwise, swap with the best child, and continue from there
                self.A[i], self.A[best] = self.A[best], self.A[i]
                i = best
            #
        #
    
    def _restore_up(self, i: int) -> None:
        """Assumes that all nodes above i satisfy the heap property.
        Restores the property for node i, by iterating over all parent nodes up from i, swapping
        any values violating the heap property. Iteration stops when reaching either the root,
        or a parent-child pair which does not violate the property."""
        
        while i > 0:
            # Determine parent node's index
            parent = (i - 1) >> 1
            
            restored = self.comp(self.A[parent], self.A[i])
            if restored:
                return
            else:
                self.A[i], self.A[parent] = self.A[parent], self.A[i]
                i = parent
            #
        #
    
    def _heapify(self) -> None:
        """Turn the values into a heap"""
        for i in reversed(range(len(self.A) // 2)):
            self._restore_down(i=i)
        #
    
    def push(self, item: T) -> None:
        """Pushes an element onto the heap"""
        self.A.append(item)
        last_ind = len(self.A) - 1
        self._restore_up(i=last_ind)
    
    def pop(self) -> T:
        """Pops an element from the heap"""
        
        # Swap first and last element (throws an IndexException if heap is empty)
        self.A[0], self.A[-1] = self.A[-1], self.A[0]
        
        # Grap the last element
        res = self.A.pop()
        self._restore_down(i=0)
        
        return res
    
    def __len__(self):
        return len(self.A)
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.A})"
    
    def __str__(self):
        return repr(self)
    
    @property
    def height(self):
        """The height of the heap"""
        n_elems = len(self)
        res = math.floor(math.log2(len(self))) + 1 if n_elems > 0 else 0
        return res
    
    def ascii_tree(self) -> str:
        return _represent_binary_tree_as_ascii(self.A)
        