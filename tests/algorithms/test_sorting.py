import random
from typing import Callable, cast, ClassVar, get_args, Iterable, Protocol
import unittest

from dsa.sorting import quicksort
from dsa.utils.types import Comparable, Conversion, Sorter


def reference_sort[T, C: Comparable](
        A: Iterable[T],
        key: Conversion[T, C]|None=None,
        reverse: bool=False,
        ) -> list[T]:
    """Just a sort function which delegates to the builtin one, for testing and stuff"""

    if key is None:
        res = sorted(cast(Iterable[Comparable], A), reverse=reverse)
        return cast(list[T], res)
    
    res = sorted(A, reverse=reverse, key=key)
    return res


def make_example_data(n_examples: int=20, n_elements: int=100, seed: int=0) -> list[list[int]]:
    rs = random.Random()
    rs.seed(seed)
    res = [
        [rs.randint(-100, 100) for _ in range(n_elements)]
        for _ in range(n_examples)
    ]
    return res


def int_key(value: int) -> tuple[int, int]:
    return (int(value % 2 == 0), value)


class TestSorting(unittest.TestCase):
    data: list[list[int]]
    sorter = staticmethod(reference_sort)

    def setUp(self) -> None:
        self.data = make_example_data() + []
        return super().setUp()

    def _compare[T](self, a: list[T], b: list[T]) -> None:
        self.assertListEqual(a, b)

    def test_standard_sorting(self) -> None:
        for numbers in self.data:
            self._compare(self.sorter(numbers), sorted(numbers))

    # !!!
    # def test_key_sorting(self) -> None:
    #     for numbers in self.data:
    #         self._compare(self.sorter(numbers, key=int_key), sorted(numbers, key=int_key))


class TestQuickSort(TestSorting):
    sorter = staticmethod(quicksort.quicksort)

    def test_standard_sorting(self) -> None:
        for numbers in self.data:
            self._compare(self.sorter(numbers), sorted(numbers))
        #
    
    def test_pivot_strategies(self) -> None:
        for strategy in get_args(quicksort.PivotStrategy.__value__):
            print(strategy)
            for numbers in self.data:
                sorted_ = self.sorter(numbers, pivot_strategy=strategy)
                self._compare(sorted_, sorted(numbers))