# Add code here for type checking.
from dsa.sorting.heapsort import heapsort
from dsa.sorting.quicksort import quicksort

from ..utils import NonComparable


def intkey(elem: int) -> int:
    return 2*elem


list_int = [1, 2, 3]
list_str = ["a", "b", "c"]
list_noncom = [NonComparable(val) for val in list_int]

### Check quicksort

# These should work
quicksort(list_int)
quicksort(list_int, key=None)
quicksort(list_str)
quicksort(list_noncom, key=NonComparable.value_key)
quicksort(list_int, key=intkey)
# These should not
quicksort(list_noncom)  # type: ignore
quicksort(list_noncom, key=None)  # type: ignore

### Check heapsort

# These should work
heapsort(list_int)
heapsort(list_int, key=None)
heapsort(list_str)
heapsort(list_noncom, key=NonComparable.value_key)
heapsort(list_int, key=intkey)
# These should not
heapsort(list_noncom)  # type: ignore
heapsort(list_noncom, key=None)  # type: ignore