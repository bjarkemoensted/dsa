from dsa.data_structures.heap_operations import _heapify, _restore_downwards
from dsa.sorting.sorter_class import Sorter
from dsa.utils.types import Comparison


@Sorter
def heapsort[T](
        A: list[T],
        constraint: Comparison[T]
        ) -> None:
    """Heapsort. Follows CLRS section 6.4 excpet
    1) uses a generic constraint function f such that f(parent, child) must be true, and
    2) uses a min-heap (with default constraint <=) for consistency with other sorting algorithms.
        The end result is then reversed (normal heapsort uses a max-heap, this implementation
        uses a min-heap and thus sorts in reverse order)"""

    _heapify(A, constraint)

    heap_size = len(A)
    for i in reversed(range(1, len(A))):
        A[0], A[i] = A[i], A[0]
        heap_size -= 1
        _restore_downwards(A, 0, constraint, stopat=heap_size)

    A.reverse()
