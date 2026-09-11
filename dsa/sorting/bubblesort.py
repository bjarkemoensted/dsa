from dsa.sorting.sorter_class import Sorter
from dsa.utils.types import Comparison


@Sorter
def bubblesort[T](
        A: list[T],
        constraint: Comparison[T],
        ) -> None:
    """Bubble sort. Same as CLRS, problem 2-2.
    First loop iteration moves the minimum element to index 0, second moves the next to index 1, etc.
    Terminates if list is determined to be ordered while sorting."""

    done = False
    for i in range(len(A)):
        done = True
        for j in reversed(range(i+1, len(A))):
            in_order = constraint(A[j-1], A[j])
            if not in_order:
                done = False
                A[j-1], A[j] = A[j], A[j-1]
            #
        if done:
            return

