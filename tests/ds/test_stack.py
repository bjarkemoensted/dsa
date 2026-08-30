import unittest

from dsa.data_structures.linear.stack import Stack

from .linear_basic_tests import TestLinear


class BasicStackTest(TestLinear):    
    def create_data_structure(self, *args: object, **kwargs: object) -> Stack[int]:
        return Stack(*args, **kwargs)  # type: ignore


class StackTest(unittest.TestCase):    
    def setUp(self) -> None:
        self.stack: Stack[int] = Stack()
        return super().setUp()
    
    def test_reversion(self) -> None:
        vals = list(range(20))
        for val in vals:
            self.stack.push(val)
        
        self.assertEqual(self.stack.to_list(), vals)
        
        recovered = []
        while self.stack.size() > 0:
            recovered.append(self.stack.pop())
        
        self.assertEqual(recovered, vals[::-1])

    def test_underflow(self) -> None:
        self.assertRaises(RuntimeError, self.stack.pop)
    
    def test_overflow(self) -> None:
        stack: Stack[int] = Stack(maxsize=0)
        val = 42
        self.assertRaises(RuntimeError, stack.push, val)
    
    def test_push_and_pop(self) -> None:
        val = 42
        self.stack.push(val)
        
        returned = self.stack.pop()
        self.assertEqual(val, returned)
    
    def test_size_methods(self) -> None:
        stack: Stack[int] = Stack(maxsize=1)
        self.assertTrue(stack.empty())
        self.assertFalse(stack.full())
        
        stack.push(42)
        self.assertTrue(stack.full())
        self.assertFalse(stack.empty())
