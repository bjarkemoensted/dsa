"""A heap implementation where the heap is implemented in a class of its own.
This is a bit more cumbersome in some regards, but also has advantages. For example, options such as min vs max heap,
and choice of a key function, are only passed once, when initializing a heap instance. This reduces the risk of forgetting
to pass one or the other when e.g. pushing or popping elements, which can lead to violations of the heap property."""

import math
from collections.abc import Callable, Iterable

from dsa.data_structures.heap_operations import (
    MIN_HEAP_DEFAULT,
    Comparable,
    _represent_binary_tree_as_ascii,
    iterate_parent_child_pairs,
)


class Comparison[T]:
    """Callable for comparing objects, optionally using a key function"""

    def __init__(self, min_: bool=True, key: Callable[[T], Comparable] | None = None) -> None:
        """Make a comparison object.
        min_: Whether to return a <= b (default).
        key: Optional callable for controlling the order"""

        self.key = key
        self.min_ = min_

    def get_vals(self, a: T, b: T) -> tuple[Comparable, Comparable]:
        """Get comparable values from two inputs"""
        if self.key is None:
            # If no comparison key, ensure that the objects support comparison
            assert isinstance(a, Comparable)
            assert isinstance(b, Comparable)
            return a, b
        else:
            # Otherwise, run them through the key function
            return self.key(a), self.key(b)

    def __call__(self, a: T, b: T) -> bool:
        val_a, val_b = self.get_vals(a, b)
        if self.min_:
            return val_a <= val_b
        else:
            return val_a >= val_b


class Heap[T]:
    """Implements a Heap class. The class supports both min- and max-heaps, and accepts an arbitrary key function, maintaining
    the heap invariant on the result of applying the function to elements on the heap.
    In other words, a standard min-heap will maintain the invariant parent <= child for all parent-child pairs, but if a key function f
    is provided, the invariant will instead be f(parent) <= f(child)."""
    
    A: list[T]
    
    def __init__(self, values: Iterable[T]|None=None, min_heap: bool=MIN_HEAP_DEFAULT, key=None):
        """values: optional iterable of elements with which to initialize the heap.
        min_: Whether to use a min-heap (defaults to True).
        key: Optional callable to apply to elements before comparing (for basing the heap structure
            on some function of its elements)"""
        
        self.A = [v for v in values] if values is not None else []
        self.min_heap = min_heap
        self.key = key
        self.comp: Comparison[T] = Comparison(min_=min_heap, key=key)
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
    
    def _heapify(self) -> None:
        """Turn the values into a heap"""
        for i in reversed(range(len(self.A) // 2)):
            self._restore_down(i=i)
    
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
        