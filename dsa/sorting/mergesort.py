from typing import Any

from dsa.sorting.sorter_class import Sorter
from dsa.utils.types import Comparison


def rearrange_inplace(A: list[Any], inds: dict[int, int], copy_inds: bool=True) -> None:
    """Rearranges A in-place, using the input indices.
    Works by going over every index i in A, then following the cycle of indices starting
    from i. For every pair of indices u, v along the cycle we then set A[u] <- A[v],
    setting inds[u] = u for denote that the cycle containing that index has been processed.
    inds is a dict {i: j, ...} indicating that A[i] after rearranging, should be the value of 
    A[j] before rearranging.
    If copy_inds = True (default), the indices are first copied to avoid modifying the list passed
    into this function. Otherwise, note that inds is being altered by this function.

    Example:
    A = [1,2,3], inds={0: 1, 1: 2, 2: 0} -> [2, 3, 1]
    """

    if not inds:
        return
    
    if copy_inds:
        inds = inds.copy()

    for cycle_start in inds:
        u = cycle_start
        # Already done if there's no cycle starting at u
        already_done = inds[u] == cycle_start
        if already_done:
            continue

        # Grab the element from the cycle start. We'll insert this at the cycle end
        elem = A[cycle_start]
        n_steps = 0  # bad inds can cause infinite loops. Count steps to raise error in that case

        while True:
            v = inds[u]
            
            # Mark first index as processed
            inds[u] = u

            # We're done if we've made it back to the beginning of the cycle
            if v == cycle_start:
                # End by setting the element we grabbed at the start of the cycle
                A[u] = elem
                break

            A[u] = A[v]
            u = v

            # Error if the cycle length exceeds the array length
            n_steps += 1
            if n_steps > len(A):
                raise ValueError("Invalid indices")


def _merge_inplace[T](
        A: list[T],
        constraint: Comparison[T],
        p: int,
        r: int,
        cut: int
    ) -> None:
    """Merges two subarrays (A[p:cut] and A[cut:r]) in-place.
    Each subarray is assumed to already be sorted."""

    # Keep track of indices to swap ({u: v} means A[u] <- A[v] after merging)
    inds: dict[int, int] = {}

    # Indices of the leftmost (smallest, with default sorting) elements of left and right subarrays
    ind_a = p
    ind_b = cut

    for k in range(p, r):
        # If the left/right subarray has run out of elements, take the smallest element from the other
        if ind_a >= cut:
            inds[k] = ind_b
            ind_b += 1
            continue
        elif ind_b >= r:
            inds[k] = ind_a
            ind_a += 1
            continue

        # If left+right subarr have elements, check if they're in order (left <= right for standard sorting)
        in_order = constraint(A[ind_a], A[ind_b])
        if in_order:
            inds[k] = ind_a
            ind_a += 1
        else:
            inds[k] = ind_b
            ind_b += 1
        #

    # inds now describes the required reassignments to sort the subarray. Apply them in-place
    rearrange_inplace(A, inds, copy_inds=False)


def _mergesort[T](
        A: list[T],
        constraint: Comparison[T],
        p: int=0,
        r: int=-1
        ) -> None:
    """Mergesort.
    Departs from CLRS (section 2.3.1) in multiple ways.
    * Merges array in-place instead of creating new arrays
    * Doesn't use the sentinel trick, but works instead with moving pointers to the
    leftmost yet-unmerged element in the left/right subarrays."""

    # If right side is not specified, default to the end of the array
    if r == -1:
        r = len(A)

    # Arrays with zero or one elements are already sorted (base case)
    if r - p <= 1:
        return

    # Divide into left and right subarrays
    cut = (p + r) // 2
    _mergesort(A, constraint, p, cut)
    _mergesort(A, constraint, cut, r)

    # Merge the subarrays. Each is already sorted from the recursion
    _merge_inplace(
        A=A,
        constraint=constraint,
        p=p,
        r=r,
        cut=cut
    )


mergesort = Sorter(_mergesort)
