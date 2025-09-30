import itertools
import math
from typing import (
    Callable,
    Iterator,
    Optional,
    Protocol,
    Sequence,
    TypeAlias,
    TypeVar,
    runtime_checkable
)


# Whether to default to using min-heaps (set to False to use max-heap as default)
MIN_HEAP_DEFAULT: bool = True

# Typevar for making a protocol for types that are 'comparable', i.e. supports stuff like a <= b
_P = TypeVar("_P", contravariant=True)

# Type for key functions for comparing a function of elements instead of direct comparison
keytype: TypeAlias = Callable


@runtime_checkable
class Comparable(Protocol[_P]):
    """This can be used as a constraint on a TypeVar to tell the type checker that
    a value will be of a type which supports comparison operators"""

    def __lt__(self, other: _P) -> bool: ...
    def __le__(self, other: _P) -> bool: ...
    def __gt__(self, other: _P) -> bool: ...
    def __ge__(self, other: _P) -> bool: ...


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


def iterate_levels(size: int) -> Iterator[list[int]]:
    """Yields for each leven in a tree a list of the indices representing nodes at that level."""
    
    if size == 0:
        return
    
    current = [0]
    while current:
        yield current
        child_inds = [fun(ind) for ind in current for fun in (_left, _right)]
        current = [child for child in child_inds if child < size]
    #


def _represent_binary_tree_as_ascii(A: list[_P], padding=" ") -> str:
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


def _satisfies_heap_property(A: Sequence[C], min_heap=MIN_HEAP_DEFAULT, key: Optional[keytype]=None) -> bool:
    """Checks if a sequence of values satisfies the heap property: parent <= child for all parent/child pairs.
    The property is checked for all elements."""
    
    if not A:
        return True
    
    for parent, child in iterate_parent_child_pairs(len(A)):
        a, b = (A[parent], A[child]) if key is None else (key(A[parent]), key(A[child]))
        pair_sat = a <= b if min_heap else a >= b
        if not pair_sat:
            return False
        #
    
    return True


def _restore_downwards(A: list[C], i: int, stopat: int=-1, min_heap=MIN_HEAP_DEFAULT, key: Optional[keytype]=None):
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
            a, b = (A[ci], A[best]) if key is None else (key(A[ci]), key(A[best]))
            child_is_better = a < b if min_heap else a > b
            if child_is_better:
                best = ci
            #
        
        if best == i:
            return
        
        A[i], A[best] = A[best], A[i]
        i = best
    #


def _restore_upwards(A: list[C], i: int, min_heap=MIN_HEAP_DEFAULT, key: Optional[keytype]=None) -> None:
    """Assumes that all parent nodes of i satisfy the heap property, but the element at i
    might violate it.
    Repeatedly swaps values with parent nodes until the heap property is restored."""
    
    while i > 0:
        parent_ind = _parent(i)
        
        a, b = (A[i], A[parent_ind]) if key is None else (key(A[i]), key(A[parent_ind]))
        violated = a < b if min_heap else a > b
        if violated:
            A[i], A[parent_ind] = A[parent_ind], A[i]
            i = parent_ind
        else:
            return
        #
    #

def heapify(A: list[C], min_heap=MIN_HEAP_DEFAULT, key: Optional[keytype]=None) -> None:
    """Turns input list into a heap"""
    for i in reversed(range(len(A) // 2)):
        _restore_downwards(A, i, min_heap=min_heap, key=key)
    #


def heappush(A: list[C], item, min_heap=MIN_HEAP_DEFAULT, key: Optional[keytype]=None) -> None:
    """Push an element onto the heap. Assumes the heap property is already satisfied."""
    # Insert at the end
    A.append(item)
    ind = len(A) - 1
    # Restore heap property of parents
    _restore_upwards(A, ind, min_heap=min_heap, key=key)


def heappop(A: list[C], min_heap=MIN_HEAP_DEFAULT, key: Optional[keytype]=None) -> C:
    """Pops an element from a heap."""
    # If we pop the only remaining element, just return that
    temp = A.pop()
    if not A:
        return temp
    
    # Otherwise, swap with the root element, and restore heap property of all children
    root_ind = 0
    res = A[root_ind]
    A[root_ind] = temp
    _restore_downwards(A, i=root_ind, min_heap=min_heap, key=key)
    return res


def heapsort(A: list[C], key: Optional[keytype]=None):
    """Sorts the input elements in-place, using the heapsort algorithm"""
    heapify(A, min_heap=False, key=key)
    heap_size = len(A)
    for i in reversed(range(1, len(A))):
        A[0], A[i] = A[i], A[0]
        heap_size -= 1
        _restore_downwards(A, 0, stopat=heap_size, min_heap=False, key=key)
    #
