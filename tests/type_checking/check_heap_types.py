# Add code here for type checking.
from dsa.data_structures.heap import Heap
from dsa.data_structures.heap_operations import heapify, heappop, heappush, heapsort

from ..utils import NonComparable


def intkey(elem: int) -> int:
    return 2*elem


list_int = [1, 2, 3]
list_str = ["a", "b", "c"]
list_noncom = [NonComparable(val) for val in list_int]


### Check type checking for the heapify function
heapify(list_int)
heapify(list_str)
# Check that providing a key function produces no error
heapify(list_noncom, key=NonComparable.value_key)
# Using e.g. int, with an int -> int key should also work
heapify(list_int, key=intkey)

# Check that the type-checker can catch non-comparables passed without a key function
heapify(list_noncom)  # type: ignore
# Explicitly using None (no key) must also give an error
heapify(list_noncom, key=None)  # type: ignore

### Check heap push
heappush(list_int, 42)
heappush(list_str, "a")
heappush(list_noncom, NonComparable(0), key=NonComparable.value_key)
# Check expected errors
heappush(list_noncom, NonComparable(0))  # type: ignore
heappush(list_noncom, NonComparable(0), key=None)  # type: ignore

### Check heap pop
_popped_int: int = heappop(list_int)
_popped_str: str = heappop(list_str)
_popped_noncom: NonComparable = heappop(list_noncom, key=NonComparable.value_key)
# # Check expected errors
heappop(list_noncom, NonComparable(0))  # type: ignore
heappop(list_noncom, NonComparable(0), key=None)  # type: ignore

### Check heap sort
heapsort(list_int)
heapsort(list_str)
heapsort(list_noncom, key=NonComparable.value_key)
# Check errors
heapsort(list_noncom)  # type: ignore
heapsort(list_noncom, key=None)  # type: ignore

### Check Heap class
heap_int = Heap(list_int)
heap_str = Heap(list_str)
heap_noncom = Heap(list_noncom, key=NonComparable.value_key)

# Check errors
Heap(list_noncom)  # type: ignore
Heap(list_noncom, key=None)  # type: ignore