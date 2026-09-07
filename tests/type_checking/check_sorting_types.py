# Add code here for type checking.
from dsa.sorting.quicksort import quicksort


class NonComparable:
    def __init__(self, value: int) -> None:
        self.value = value


def key(elem: NonComparable) -> int:
    return elem.value


def intkey(elem: int) -> int:
    return 2*elem


list_int = [1, 2, 3]
list_str = ["a", "b", "c"]
list_noncom = [NonComparable(val) for val in list_int]


### These should work
quicksort(list_int)
quicksort(list_int, key=None)
quicksort(list_str)
quicksort(list_noncom, key=key)
quicksort(list_int, key=intkey)
# These should not
quicksort(list_noncom)  # type: ignore
quicksort(list_noncom, key=None)  # type: ignore
