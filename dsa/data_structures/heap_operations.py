import itertools
import math
import operator
from collections.abc import Iterator, Sequence
from typing import overload

from dsa.utils.comparison import KeyComparison
from dsa.utils.types import Comparable, Comparison, Conversion

# Whether to default to using min-heaps (set to False to use max-heap as default)
MIN_HEAP_DEFAULT: bool = True


def _determine_relation(min_heap: bool=MIN_HEAP_DEFAULT) -> Comparison:
    """Determines the relational comparison to use when comparing elements on a heap"""
    relation = operator.le if min_heap else operator.ge
    return relation


def make_constraint[T, C](min_heap: bool=MIN_HEAP_DEFAULT, key: Conversion[T, C]|None=None) -> Comparison:
    """Returns a comparison function f such that all parent-child pairs (p, c) must satisfy f(p, c)
    for the heap invariant to be satisfied.
    Examples:
    min_heap=True  --> parent <= child
    min_heap=False --> parent >= child
    min_heap = True and a key function f --> f(parent) <= f(child)
    """

    relation = _determine_relation(min_heap=min_heap)
    constraint = relation if key is None else KeyComparison(relation, key)
    return constraint


def _left(i: int) -> int:
    """Given an index, returns the index of its left child in a binary tree"""
    return 2*i + 1


def _right(i: int) -> int:
    """Given an index, returns the index of its right child in a binary tree"""
    return 2*i + 2


def _parent(i: int) -> int:
    """Given an index, returns the index of its parent in a binary tree"""
    return (i - 1) // 2


def iterate_parent_child_pairs(size: int, start_index: int=0) -> Iterator[tuple[int, int]]:
    """Iterate over pairs of parent/child indices in a binary heap.
    size is the length of the list/array holding the values.
    start_index represents the index at which to start the iteration (defaults to the root
    node at index 0)"""
    
    if not (0 <= start_index < size):
        raise ValueError(f"Iteration must start at indices between 0 and size ({size}). Got {start_index}")    
    
    child_inds = (_left(start_index), _right(start_index))
    for i in child_inds:
        if i < size:
            yield start_index, i
            yield from iterate_parent_child_pairs(size, i)


def iterate_levels(size: int) -> Iterator[list[int]]:
    """Yields for each leven in a tree a list of the indices representing nodes at that level."""
    
    if size == 0:
        return
    
    current = [0]
    while current:
        yield current
        child_inds = [fun(ind) for ind in current for fun in (_left, _right)]
        current = [child for child in child_inds if child < size]


def _represent_binary_tree_as_ascii(A: list, padding: str=" ") -> str:
    """Represents a binary tree as ASCII.
    Works by defining an empty line for each level in the tree, then representing the root
    at the middle of the topmost row, then repeatedly adding left and right children at the
    middle of the left and right sides of the next level."""
    
    if not A:
        return "<empty>"
    
    # Convert elements to strings and determine the number of characters needed to display each elem
    A_s = [str(val) for val in A]
    n_chars = max(map(len, A_s))
    # We need to assign 2**n - 1 elems at the bottom row
    n_elems = next(m for m in (2**n - 1 for n in itertools.count(1)) if m >= len(A_s))

    # Container for ascii lines and skip size (horizontal distance to child nodes)
    skip = (n_elems+1) // 2
    lines: list[str] = []
    
    # tuples of (index in heap, index in ascii row). Start with just the root node
    seeds = [(0, (n_elems - 1) // 2)]
    next_ = []
    
    while seeds:
        skip = skip // 2
        line = n_elems*[n_chars*padding]
        for ai, di in seeds:
            # Start by adding the values at the current level
            halfdiff = (n_chars - len(A_s[ai])) / 2
            # Pad to ensure consistent width
            sym = math.ceil(halfdiff)*padding + A_s[ai] + math.floor(halfdiff)*padding
            line[di] = sym
            
            # add child nodes for next level
            for direction, fun in ((-1, _left), (+1, _right)):
                child = fun(ai)
                if not 0 <= child < len(A_s):
                    continue  # skip child indices that fall off A
                next_.append((child, di + direction*skip))
        
        lines.append("".join(line))
        seeds = next_
        next_ = []
        
    res = "\n".join(lines)
    
    return res


def _satisfies_heap_property[T](
    A: Sequence[T],
    constraint: Comparison[T] 
    ) -> bool:
    """Determines whether the sequence A satisfies the heap invariant with the input constraint"""

    if not A:
        return True

    for parent, child in iterate_parent_child_pairs(len(A)):
        heap_property_satisfied = constraint(A[parent], A[child])
        if not heap_property_satisfied:
            return False
        #
    
    return True


def _restore_downwards[T](
        A: list[T],
        i: int,
        constraint: Comparison[T],
        stopat: int=-1,
        ) -> None:
    """Assumes that child nodes of i already satisfy the heap property, but that the node at i
    might violate it.
    Allow the node to float down the heap, by swapping places with its largest child."""
    
    if stopat == -1:
        stopat = len(A)
    
    while True:
        child_inds = (_left(i), _right(i))
        parent_ind = i
        for child_ind in child_inds:
            if child_ind >= stopat:
                continue

            parent_val = A[parent_ind]
            child_val = A[child_ind]

            heap_property_satisfied = constraint(parent_val, child_val)
            if not heap_property_satisfied:
                parent_ind = child_ind

        
        if parent_ind == i:
            return
        
        A[i], A[parent_ind] = A[parent_ind], A[i]
        i = parent_ind


def _restore_upwards[T](
        A: list[T],
        i: int,
        constraint: Comparison[T]
        ) -> None:
    """Assumes that all parent nodes of i satisfy the heap property, but the element at i
    might violate it.
    Repeatedly swaps values with parent nodes until the heap property is restored."""
    
    while i > 0:
        parent_ind = _parent(i)
        child_val = A[i]
        parent_val = A[parent_ind]
        heap_property_satisfied = constraint(parent_val, child_val)
        if not heap_property_satisfied:
            A[i], A[parent_ind] = A[parent_ind], A[i]
            i = parent_ind
        else:
            return


def _heapify[T](A: list[T], constraint: Comparison[T]) -> None:
    """Turns input list into a heap"""
    for i in reversed(range(len(A) // 2)):
        _restore_downwards(A, i, constraint)


@overload
def heapify[C: Comparable](A: list[C], min_heap: bool = ..., key: None = ...) -> None: ...
@overload
def heapify[T, C](A: list[T], min_heap: bool, key: Conversion[T, C]) -> None: ...
@overload
def heapify[T, C](A: list[T], min_heap: bool = ..., *, key: Conversion[T, C]) -> None: ...
def heapify[T, C](A: list, min_heap: bool=MIN_HEAP_DEFAULT, key: Conversion[T, C]|None=None) -> None:
    """Turns input list into a heap"""
    constraint = make_constraint(min_heap=min_heap, key=key)
    return _heapify(A, constraint)


def _heappush[T](A: list[T], item: T, constraint: Comparison[T]) -> None:
    """Push an element onto the heap. Assumes the heap property is already satisfied."""
    # Insert at the end
    A.append(item)
    ind = len(A) - 1
    # Restore heap property of parents
    return _restore_upwards(A, ind, constraint=constraint)


@overload
def heappush[C: Comparable](A: list[C], item: C, *, min_heap: bool=..., key: None=...) -> None: ...
@overload
def heappush[T, C](A: list[T], item: T, min_heap: bool, key: Conversion[T, C]) -> None: ...
@overload
def heappush[T, C](A: list[T], item: T, min_heap: bool=..., *, key: Conversion[T, C]) -> None: ...
def heappush[T, C](A: list, item: T, min_heap: bool=MIN_HEAP_DEFAULT, key: Conversion[T, C]|None=None) -> None:
    """Push an element onto the heap. Assumes the heap property is already satisfied.
    A: List containing the heap elements
    item: The element to push onto the heap
    min_heap: Whether to use a min_heap (as opposed to max-heap)
    key: Optional key function to apply to elements before checking the heap property on a parent-child pair"""

    # Determine whether to require parent <= child (min heap) or parent >= child (max heap)
    constraint = make_constraint(min_heap=min_heap, key=key)

    return _heappush(A, item, constraint)


def _heappop[T](A: list[T], constraint: Comparison[T]) -> T:
    """Pops an element from a heap."""
    # If we pop the only remaining element, just return that
    temp = A.pop()
    if not A:
        return temp
    
    # Otherwise, swap with the root element, and restore heap property of all children
    root_ind = 0
    res = A[root_ind]
    A[root_ind] = temp
    _restore_downwards(A, root_ind, constraint)

    return res



@overload
def heappop[C: Comparable](A: list[C], min_heap: bool = ..., key: None = ...) -> C: ...
@overload
def heappop[T, C](A: list[T], min_heap: bool, key: Conversion[T, C]) -> T: ...
@overload
def heappop[T, C](A: list[T], min_heap: bool = ..., *, key: Conversion[T, C]) -> T: ...
def heappop[T, C](
    A: list,
    min_heap: bool = MIN_HEAP_DEFAULT,
    key: Conversion[T, C] | None = None,
) -> T:
    """Pops an element from a heap."""

    constraint = make_constraint(min_heap=min_heap, key=key)
    res = _heappop(A, constraint)
    return res


@overload
def heapsort[C: Comparable](A: list[C], key: None = ...) -> None: ...
@overload
def heapsort[T, C](A: list[T], key: Conversion[T, C]) -> None: ...
@overload
def heapsort[T, C](A: list[T], *, key: Conversion[T, C]) -> None: ...
def heapsort[T, C](A: list, key: Conversion[T, C]|None=None) -> None:
    """Sorts the input elements in-place, using the heapsort algorithm"""

    constraint = make_constraint(min_heap=False, key=key)
    _heapify(A, constraint)

    heap_size = len(A)
    for i in reversed(range(1, len(A))):
        A[0], A[i] = A[i], A[0]
        heap_size -= 1
        _restore_downwards(A, 0, constraint, stopat=heap_size)
