import random
import unittest
from typing import Any, Callable, Iterable, cast, get_args

from dsa.sorting import quicksort
from dsa.utils.types import Comparable, Conversion


def make_example_data(n_examples: int=20, n_elements: int=100, seed: int=0) -> list[list[int]]:
    rs = random.Random()
    rs.seed(seed)
    res = [
        [rs.randint(-100, 100) for _ in range(n_elements)]
        for _ in range(n_examples)
    ]
    return res


def int_key(value: int) -> tuple[int, int]:
    """Example of a key function that maps integers to sortable tuples"""
    return (int(value % 2 == 0), value)


class TestSorting(unittest.TestCase):
    data: list[list[int]]

    @staticmethod
    def sort[T](A: list[T], key: Callable|None=None, reverse: bool=False) -> list[T]:
        if key is None:
            res = sorted(cast(Iterable[Comparable], A), reverse=reverse)
            return cast(list[T], res)
        else:
            return sorted(A, key=key, reverse=reverse)
        
    def setUp(self) -> None:
        self.data = make_example_data() + []
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

    def test_key_sorting(self) -> None:
        for numbers in self.data:
            ordered = self.sort(numbers, key=int_key)
            self.check_sorted(ordered, key=int_key)


class TestQuickSort(TestSorting):
    sorter = quicksort.quicksort

    def test_standard_sorting(self) -> None:
        for numbers in self.data:
            self.check_sorted(self.sorter(numbers))
        #
    
    def test_pivot_strategies(self) -> None:
        for strategy in get_args(quicksort.PivotStrategy.__value__):
            print(strategy)
            for numbers in self.data:
                sorted_ = self.sorter(numbers, pivot_strategy=strategy)
                self.check_sorted(sorted_)
