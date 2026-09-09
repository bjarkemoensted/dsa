import unittest
from copy import deepcopy
from typing import Any, Callable, Iterable, Protocol, cast, get_args

from dsa.sorting import heapsort, quicksort, sorter_class
from dsa.utils.randomization import make_random_state
from dsa.utils.types import Comparable, Conversion

from ..utils import NonComparable, make_integers


class SortFunc[**P](Protocol):
    """Represents a generic sorting function.
    This is just to be able to type hint builtin sorted along with Sorter instances"""
    def __call__[T](
        self,
        A: list[T],
        key: Callable|None=None,
        reverse: bool=False,
        *args: P.args,
        **kwargs: P.kwargs
    ) -> list[T]: ...


def _default_sort[T](A: list[T], key: Callable|None=None, reverse: bool=False) -> list[T]:
    if key is None:
        res = sorted(cast(Iterable[Comparable], A), reverse=reverse)
        return cast(list[T], res)
    else:
        return sorted(A, key=key, reverse=reverse)


def int_key(value: int) -> tuple[int, int]:
    """Example of a key function that maps integers to sortable tuples"""
    return (int(value % 2 == 0), value)


class TestSorting(unittest.TestCase):
    data: list[list[int]]
    sort: SortFunc|sorter_class.Sorter = staticmethod(_default_sort)
        
    def setUp(self) -> None:
        rs = make_random_state(0)
        edge_cases = [[], [1], [1, 2]]
        cases = [make_integers() for _ in range(100)]
        self.data = cases + edge_cases
        self.noncom_data = [[NonComparable(value=n, other_value=rs.randint(0, 10)) for n in case] for case in cases]
        return super().setUp()

    def check_sorted[T](self, A: list[T], key: Conversion[T, Any]|None=None, reverse: bool=False) -> None:
        for i in range(len(A)-1):
            a, b = A[i], A[i+1]
            if key is None:
                val_a, val_b = a, b
            else:
                val_a, val_b = key(a), key(b)

            assert isinstance(val_a, Comparable)
            assert isinstance(val_b, Comparable)

            if reverse:
                self.assertGreaterEqual(val_a, val_b, f"Disorder at {i=}: {val_a=}, {val_b=}")
            else:
                self.assertLessEqual(val_a, val_b, f"Disorder at {i=}: {val_a=}, {val_b=}")

    def test_standard_sorting(self) -> None:
        for numbers in self.data:
            self.check_sorted(self.sort(numbers))

    def test_reverse_sorting(self) -> None:
        for numbers in self.data:
            reverse_order = self.sort(numbers, reverse=True)
            ordered = list(reversed(reverse_order))
            self.check_sorted(ordered)

    def test_key_sorting_int(self) -> None:
        for numbers in self.data:
            ordered = self.sort(numbers, key=int_key)
            self.check_sorted(ordered, key=int_key)

    def test_key_sorting_noncomparable(self) -> None:
        """Check that sorting non-comparables works with an appropriate key function"""
        for objects in self.noncom_data:
            ordered = self.sort(objects, key=NonComparable.value_key)
            self.check_sorted(ordered, key=NonComparable.value_key)


class TestQuickSort(TestSorting):
    sort = quicksort.quicksort

    def test_standard_sorting(self) -> None:
        for numbers in self.data:
            self.check_sorted(self.sort(numbers))
        #
    
    def test_pivot_strategies(self) -> None:
        for strategy in get_args(quicksort.PivotStrategy.__value__):
            print(strategy)
            for numbers in self.data:
                sorted_ = self.sort(numbers, pivot_strategy=strategy)
                self.check_sorted(sorted_)

    def test_random_seed_affects_sorting(self) -> None:
        """Run quicksort on non-comparables with the same value (which randomises the
        final order). Check that different random seeds result in different final orderings"""

        rs = make_random_state(0)
        n = 1000
        elems = [NonComparable(value=0, other_value = rs.randint(0, 100)) for _ in range(n)]

        def sort_(seed: int|None) -> list[int]:
            """Sorts the non-comparables according to .value.
            Returns a list of the .other_value of each element,
            in the sorted order."""
            A = deepcopy(elems)
            _ordered = self.sort(
                A=A,
                key=NonComparable.value_key,
                pivot_strategy="random",
                seed=seed
            )
            return [elem.other_value for elem in _ordered]
        
        # We should get the same order when using the same seed
        self.assertListEqual(sort_(1), sort_(1))
        # Using different seeds or None (for large lists) should give difference orderings
        self.assertNotEqual(sort_(1), sort_(2))
        self.assertNotEqual(sort_(None), sort_(None))
        
        
class TestHeapSort(TestSorting):
    sort = heapsort.heapsort
