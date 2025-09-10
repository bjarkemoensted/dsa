import unittest

from dsa.data_structures import Stack

from .linear_basic_tests import TestLinear



class BasicStackTest(TestLinear):    
    def create_data_structure(self, *args, **kwargs) -> Stack[int]:
        return Stack(*args, **kwargs)
    
    def insert(self, data: Stack, val):
        return data.push(val)
    
    def delete(self, data: Stack):
        return data.pop()


class StackTest(unittest.TestCase):    
    def setUp(self) -> None:
        self.stack: Stack[int] = Stack()
        return super().setUp()
    
    def test_reversion(self):
        vals = list(range(20))
        for val in vals:
            self.stack.push(val)
        
        self.assertEqual(self.stack.to_list(), vals)
        
        recovered = []
        while self.stack.size() > 0:
            recovered.append(self.stack.pop())
        
        self.assertEqual(recovered, vals[::-1])

    def test_underflow(self):
        self.assertRaises(RuntimeError, self.stack.pop)
    #
    
    def test_overflow(self):
        stack = Stack(maxsize=0)
        val = 42
        self.assertRaises(RuntimeError, stack.push, val)
    
    def test_push_and_pop(self):
        val = 42
        self.stack.push(val)
        
        returned = self.stack.pop()
        self.assertEqual(val, returned)
    
    def test_size_methods(self):
        stack = Stack(maxsize=1)
        self.assertTrue(stack.empty())
        self.assertFalse(stack.full())
        
        stack.push(42)
        self.assertTrue(stack.full())
        self.assertFalse(stack.empty())
    #
