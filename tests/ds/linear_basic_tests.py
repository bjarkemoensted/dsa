import unittest
from abc import ABC, abstractmethod
from collections import Counter
from copy import deepcopy
from typing import Any

from dsa.data_structures.linear.base import BaseContainer


class TestLinear[L: BaseContainer](ABC, unittest.TestCase):
    """For running some standard tests, which are presumed to be similar across different
    types of linear structures like stacks, queues, etc."""

    @staticmethod
    def put(container: L, item: Any) -> None:
        raise NotImplementedError

    @staticmethod
    def get(container: L) -> Any:
        raise NotImplementedError

    @classmethod
    def setUpClass(cls) -> None:
        required = (
            "put",
            "get"
        )

        missing = [attr for attr in required if attr not in cls.__dict__]
        if missing:
            raise RuntimeError(f"Test subclass is missing: {', '.join(missing)}")
        return super().setUpClass()

    data: L
    data_bounded: L
    
    vals_ = tuple(range(50))
    bounded_maxsize = 32

    def test_is_full(self) -> None:
        for val in range(self.data_bounded.maxsize):
            self.put(self.data_bounded, val)
        self.assertTrue(self.data_bounded.full())

    def test_insertion(self) -> None:
        for i, val in enumerate(self.vals_):
            size_exp = i + 1
            self.put(self.data, val)
            self.assertTrue(self.data.size() == size_exp)

            if size_exp > self.data_bounded.maxsize:
                with self.assertRaises(RuntimeError):
                    self.put(self.data_bounded, val)
            else:
                self.put(self.data_bounded, val)
            self.assertEqual(self.data_bounded.size(), min(size_exp, self.data_bounded.maxsize))
    
    def test_deletion(self) -> None:
        for val in self.vals_:
            self.put(self.data, val)
            
        n_elems = self.data.size()
        for _ in range(n_elems):
            self.get(self.data)
            n_elems -= 1
            self.assertEqual(n_elems, self.data.size())
    
    def test_overflow(self) -> None:
        for val in range(self.data_bounded.maxsize):
            self.put(self.data_bounded, val)
        
        self.assertTrue(self.data_bounded.full())
        
        with self.assertRaises(RuntimeError):
            self.put(self.data_bounded, 42)
    
    def test_underflow(self) -> None:
        self.assertTrue(self.data.empty())

        with self.assertRaises(RuntimeError):
            self.get(self.data)
    
    def test_to_list(self) -> None:
        for i in range(len(self.vals_)):
            subvals = list(self.vals_[:i])
            q = deepcopy(self.data)
            for val in subvals:
                self.put(q, val)
            
            list_ = q.to_list()
            # Compare the number of occurrences of each element to compare unordered
            value_counts_expected = sorted(Counter(subvals).items())
            value_counts_retrieved = sorted(Counter(list_).items())
            self.assertEqual(value_counts_expected, value_counts_retrieved)
            
            self.assertEqual(len(list_), q.size())
    
    @abstractmethod
    def create_data_structure(self, *args: object, **kwargs: object) -> L:
        raise NotImplementedError
    
    def setUp(self) -> None:
        self.data = self.create_data_structure()
        self.data_bounded = self.create_data_structure(maxsize=self.bounded_maxsize)
