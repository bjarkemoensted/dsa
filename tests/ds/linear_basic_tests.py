from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Generic, TypeVar
import unittest

from dsa.data_structures.linear_structures import Stack, Queue, LinearBase

T = TypeVar("T")
L = TypeVar("L", bound=LinearBase)


class TestLinear(ABC, unittest.TestCase, Generic[T, L]):
    """For running some standard tests, which are presumed to be similar across different
    types of linear structures like stacks, queues, etc."""
    
    data: L
    data_bounded: L
    
    vals_ = tuple(range(50))
    bounded_maxsize = 32

    @abstractmethod
    def insert(self, data_: L, val):
        raise NotImplementedError
    
    @abstractmethod
    def delete(self, data_: L) -> T:
        raise NotImplementedError

    def test_is_full(self):
        for val in range(self.data_bounded.maxsize):
            self.insert(self.data_bounded, val)
        self.assertTrue(self.data_bounded.full())

    def test_insertion(self):
        for i, val in enumerate(self.vals_):
            size_exp = i + 1
            self.insert(self.data, val)
            self.assertTrue(self.data.size() == size_exp)
            
            if size_exp > self.data_bounded.maxsize:
                with self.assertRaises(RuntimeError):
                    self.insert(self.data_bounded, val)
                #
            else:
                self.insert(self.data_bounded, val)
            self.assertEqual(self.data_bounded.size(), min(size_exp, self.data_bounded.maxsize))
        #
    
    def test_deletion(self):
        for val in self.vals_:
            self.insert(self.data, val)
        
        n_elems = self.data.size()
        for _ in range(n_elems):
            self.delete(self.data)
            n_elems -= 1
            self.assertEqual(n_elems, self.data.size())
    
    def test_overflow(self):
        for val in range(self.data_bounded.maxsize):
            self.insert(self.data_bounded, val)
        
        self.assertTrue(self.data_bounded.full())
        
        with self.assertRaises(RuntimeError):
            self.insert(self.data_bounded, 42)
    
    def test_underflow(self):
        self.assertTrue(self.data.empty())

        with self.assertRaises(RuntimeError):
            self.delete(self.data)
    
    def test_to_list(self):
        for i in range(len(self.vals_)):
            subvals = list(self.vals_[:i])
            q = deepcopy(self.data)
            for val in subvals:
                self.insert(q, val)
            
            list_ = q.to_list()
            self.assertEqual(list_, subvals)
            
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


class BasicStackTest(TestLinear):
    
    def create_data_structure(self, *args, **kwargs) -> Stack[int]:
        return Stack(*args, **kwargs)
    
    def insert(self, data: Stack, val):
        return data.push(val)
    
    def delete(self, data: Stack):
        return data.pop()


class BasicQueueTest(TestLinear):
    
    def create_data_structure(self, *args, **kwargs) -> Queue[int]:
        return Queue(*args, **kwargs)
    
    def insert(self, data: Queue, val):
        return data.enqueue(val)
    
    def delete(self, data: Queue):
        return data.dequeue()
    #
