from dataclasses import dataclass
import operator
from typing import Iterable, Literal, overload

from dsa.utils.types import Comparable, Comparison, Conversion
from dsa.utils.comparison import make_comparison


@dataclass
class Settings[T]:
    """Settings for the quicksort algorithm."""
    reverse: bool
    pivot_strategy: PivotStrategy
    constraint: Comparison[T]


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

        # Check loop invariants!!!
        for k in range(p, r+1):
            if p <= k <= i:
                assert constraint(A[k], x)
            if i+1 <= k <= j-1:
                assert not constraint(A[k], x)
            if k == r:
                assert A[k] == x

        if constraint(A[j], x):
            i += 1
            _swap(A, i, j)

    res = i + 1
    _swap(A, res, r)
    return res



def _quicksort[T](
        A: list[T],
        p: int,
        r: int,
        pivot_strategy,
        constraint: Comparison[T]=operator.le
        ) -> None:

    if p >= r:
        return

    q = _partition(A, p, r, pivot_strategy, constraint)

    _quicksort(A, p, q - 1, pivot_strategy, constraint)  # left part
    _quicksort(A, q + 1, r, pivot_strategy, constraint)  # right part


# TODO handle overloads or maybe a re-usable decorator func/class to resolve A, key, reverse into a constraint func
# TODO and possible handle an in-place arg as well!!!
def quicksort[T, C: Comparable](
        A: Iterable[T],
        key: Conversion[T, C]|None=None,
        reverse: bool=False,
        pivot_strategy: PivotStrategy="median",
    ) -> list[T]:

    res = list(A).copy()
    constraint = make_comparison(
        relation=operator.ge if reverse else operator.le,
        key=key
    )
    _quicksort(res, 0, len(res)-1, pivot_strategy, constraint=constraint)
    return res