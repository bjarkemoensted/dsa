from unittest import TestCase

from dsa.data_structures.stack import Stack


class StackTest(TestCase):

    def setUp(self):
        self.stack = Stack()
        return super().setUp()

    def test_underflow(self):
        self.assertRaises(RuntimeError, self.stack.pop)
    #
    
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