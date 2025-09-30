from abc import ABC, abstractmethod
from collections import Counter
from copy import deepcopy
from typing import Generic, TypeVar
import unittest

from dsa.data_structures.linear import BaseContainer


T = TypeVar("T")
L = TypeVar("L", bound=BaseContainer)


class TestLinear(ABC, unittest.TestCase, Generic[T, L]):
    """For running some standard tests, which are presumed to be similar across different
    types of linear structures like stacks, queues, etc."""
    
    data: L
    data_bounded: L
    
    vals_ = tuple(range(50))
    bounded_maxsize = 32

    def test_is_full(self):
        for val in range(self.data_bounded.maxsize):
            self.data_bounded.put(val)
        self.assertTrue(self.data_bounded.full())

    def test_insertion(self):
        for i, val in enumerate(self.vals_):
            size_exp = i + 1
            self.data.put(val)
            self.assertTrue(self.data.size() == size_exp)
            
            if size_exp > self.data_bounded.maxsize:
                with self.assertRaises(RuntimeError):
                    self.data_bounded.put(val)
                #
            else:
                self.data_bounded.put(val)
            self.assertEqual(self.data_bounded.size(), min(size_exp, self.data_bounded.maxsize))
        #
    
    def test_deletion(self):
        for val in self.vals_:
            self.data.put(val)
        
        n_elems = self.data.size()
        for _ in range(n_elems):
            self.data.get()
            n_elems -= 1
            self.assertEqual(n_elems, self.data.size())
    
    def test_overflow(self):
        for val in range(self.data_bounded.maxsize):
            self.data_bounded.put(val)
        
        self.assertTrue(self.data_bounded.full())
        
        with self.assertRaises(RuntimeError):
            self.data_bounded.put(42)
    
    def test_underflow(self):
        self.assertTrue(self.data.empty())

        with self.assertRaises(RuntimeError):
            self.data.get()
    
    def test_to_list(self):
        for i in range(len(self.vals_)):
            subvals = list(self.vals_[:i])
            q = deepcopy(self.data)
            for val in subvals:
                q.put(val)
            
            list_ = q.to_list()
            # Compare the number of occurrences of each element to compare unordered
            value_counts_expected = sorted(Counter(subvals).items())
            value_counts_retrieved = sorted(Counter(list_).items())
            self.assertEqual(value_counts_expected, value_counts_retrieved)
            
            self.assertEqual(len(list_), q.size())
        #
    #
    
    @abstractmethod
    def create_data_structure(self, *args, **kwargs) -> L:
        raise NotImplementedError
    
    def setUp(self):
        self.data = self.create_data_structure()
        self.data_bounded = self.create_data_structure(maxsize=self.bounded_maxsize)
    #
