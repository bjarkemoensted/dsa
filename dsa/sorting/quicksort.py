from typing import Literal

from dsa.sorting.sorter_class import Sorter
from dsa.utils.types import Comparison

# TODO enable random strategy
type PivotStrategy = Literal["first", "last", "median"]


def _determine_pivot_index(p: int, r: int, strategy: PivotStrategy) -> int:
    """r is the greatest index allowed, e.g. len(A) - 1"""
    match strategy:
        case "last":
            return r
        case "first":
            return p
        case "median":
            return (r + p) // 2
        case _:
            raise ValueError(f"Unsupported pivot strategy: {strategy!r}")


def _swap(A: list, i: int, j: int) -> None:
    A[i], A[j] = A[j], A[i]


def _partition[T](
        A: list[T],
        p: int,
        r: int,
        pivot_strategy: PivotStrategy,
        constraint: Comparison[T]
        ) -> int:
    """Partitions a subarray in-place so that all elements left of a pivot index i
    are <= the pivot, and elements to the right are >= the pivot.
    This follows CLRS, section 7.1.
    The pivot is selected according to the specified pivot strategy, then swapped to the
    rightmost position r of the array. Following this, the loop has the following
    invariants for various regions of the subarray:
    A[p:i] <= pivot
    A[i+1:j+1] >= pivot
    A[j:r] not yet processed
    """

    pivot_ind = _determine_pivot_index(p, r, pivot_strategy)
    _swap(A, r, pivot_ind)

    i = p - 1
    x = A[r]  # Pivot value
    for j in range(p, r):
        if constraint(A[j], x):
            i += 1
            _swap(A, i, j)

    res = i + 1
    _swap(A, res, r)
    return res


@Sorter
def quicksort[T](
        A: list[T],
        constraint: Comparison[T],
        p: int=0,
        r: int|None=None,
        pivot_strategy: PivotStrategy="median",
        ) -> None:
    """Quicksort algorithm. Follows CLRS except
    1) Uses a general constraint function which must return True for subsequent elements if ordered, and
    2) Uses a stack with the bound of yet-unsorted regions, instead of recursing"""

    # Stack with remaining region boundaries
    remaining: list[tuple[int, int]] = [
        (p, len(A)-1 if r is None else r)
    ]

    while remaining:
        p_, r_ = remaining.pop()

        # If region is empty, it's already sorted
        if p_ >= r_:
            continue

        # Partition current region around the pivot value
        q = _partition(A, p_, r_, pivot_strategy, constraint)
        # Add regions to the left and right of the final pivot location to the stack
        remaining.append((p_, q-1))
        remaining.append((q+1, r_))
