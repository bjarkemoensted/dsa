from typing import (
    Iterator,
    Protocol,
    Sequence,
    TypeVar,
    runtime_checkable
)


# Whether to default to using min-heaps (set to False to use max-heap as default)
MIN_HEAP_DEFAULT: bool = True


# Typevar for making a protocol for types that are 'comparable', i.e. supports stuff like a <= b
T = TypeVar("T", contravariant=True)


@runtime_checkable
class Comparable(Protocol[T]):
    """This can be used as a constraint on a TypeVar to tell the type checker that
    a value will be of a type which supports comparison operators"""

    def __lt__(self, other: T) -> bool: ...
    def __le__(self, other: T) -> bool: ...
    def __gt__(self, other: T) -> bool: ...
    def __ge__(self, other: T) -> bool: ...


C = TypeVar("C", bound=Comparable)


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
        #
    #


def _satisfies_heap_property(A: Sequence[C], min_heap=MIN_HEAP_DEFAULT) -> bool:
    """Checks if a sequence of values satisfies the heap property: parent <= child for all parent/child pairs.
    The property is checked for all elements."""
    
    if not A:
        return True
    
    for parent, child in iterate_parent_child_pairs(len(A)):
        pair_sat = A[parent] <= A[child] if min_heap else A[parent] >= A[child]
        if not pair_sat:
            return False
        #
    
    return True


def _restore_downwards(A: list[C], i: int, stopat: int=-1, min_heap=MIN_HEAP_DEFAULT):
    """Assumes that child nodes of i already satisfy the heap property, but that the node at i
    might violate it.
    Allow the node to float down the heap, by swapping places with its largest child."""
    
    if stopat == -1:
        stopat = len(A)
    
    while True:
        child_inds = (_left(i), _right(i))
        best = i
        for ci in child_inds:
            if ci >= stopat:
                continue
            child_is_better = A[ci] < A[best] if min_heap else A[ci] > A[best]
            if child_is_better:
                best = ci
            #
        
        if best == i:
            return
        
        A[i], A[best] = A[best], A[i]
        i = best
    #


def _restore_upwards(A: list[C], i: int, min_heap=MIN_HEAP_DEFAULT) -> None:
    """Assumes that all parent nodes of i satisfy the heap property, but the element at i
    might violate it.
    Repeatedly swaps values with parent nodes until the heap property is restored."""
    
    while i > 0:
        parent_ind = _parent(i)
        violated = A[i] < A[parent_ind] if min_heap else A[i] > A[parent_ind]
        if violated:
            A[i], A[parent_ind] = A[parent_ind], A[i]
            i = parent_ind
        else:
            return
        #
    #

def heapify(A: list[C], min_heap=MIN_HEAP_DEFAULT) -> None:
    """Turns input list into a heap"""
    for i in reversed(range(len(A) // 2)):
        _restore_downwards(A, i, min_heap=min_heap)
    #


def heappush(A: list[C], item, min_heap=MIN_HEAP_DEFAULT) -> None:
    """Push an element onto the heap. Assumes the heap property is already satisfied."""
    # Insert at the end
    A.append(item)
    ind = len(A) - 1
    # Restore heap property of parents
    _restore_upwards(A, ind, min_heap=min_heap)


def heappop(A: list[C], min_heap=MIN_HEAP_DEFAULT) -> C:
    """Pops an element from a heap."""
    # If we pop the only remaining element, just return that
    temp = A.pop()
    if not A:
        return temp
    
    # Otherwise, swap with the root element, and restore heap property of all children
    root_ind = 0
    res = A[root_ind]
    A[root_ind] = temp
    _restore_downwards(A, i=root_ind, min_heap=min_heap)
    return res


def heapsort(A: list[C]):
    """Sorts the input elements in-place, using the heapsort algorithm"""
    heapify(A, min_heap=False)
    heap_size = len(A)
    for i in reversed(range(1, len(A))):
        A[0], A[i] = A[i], A[0]
        heap_size -= 1
        _restore_downwards(A, 0, stopat=heap_size, min_heap=False)
    #
