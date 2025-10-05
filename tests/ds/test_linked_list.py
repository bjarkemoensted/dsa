import unittest

from dsa.data_structures.linear.linked_list import LinkedList, Node

from .linear_basic_tests import TestLinear


class BasicPriorityQueueTest(TestLinear):
    def create_data_structure(self, *args, **kwargs) -> LinkedList[int]:
        return LinkedList(*args, **kwargs)
    #


class TestLinkedList(unittest.TestCase):

    def setUp(self):
        self.list = LinkedList()

    def test_insert_single_element(self):
        self.list.put(10)
        
        node = self.list.search(10)
        self.assertIsNotNone(node)
        
        self.assertEqual(node.key, 10)
        self.assertIs(node.prev, self.list.nil)
        self.assertIs(node.next, self.list.nil)

    def test_insert_multiple_elements(self):
        values = [1, 2, 3]
        for v in values:
            self.list.put(v)

        for v in values:
            self.assertIsNotNone(self.list.search(v), f"Value {v} not found after insert")

        # Ensure internal linkage
        n1 = self.list.search(1)
        n2 = self.list.search(2)
        n3 = self.list.search(3)

        self.assertIs(n1.next, n2)
        self.assertIs(n2.prev, n1)
        self.assertIs(n2.next, n3)
        self.assertIs(n3.prev, n2)

    def test_search_existing_and_non_existing(self):
        self.list.put("a")
        self.list.put("b")

        found = self.list.search("a")
        with self.assertRaises(ValueError):
            _ = self.list.search("z")

        self.assertIsNotNone(found)
        self.assertEqual(found.key, "a")

    def test_delete_existing_node(self):
        for v in [1, 2, 3]:
            self.list.insert(v)

        self.list.remove(2)
        with self.assertRaises(ValueError):
            self.list.search(2)

        n1 = self.list.search(1)
        n3 = self.list.search(3)
        self.assertIs(n1.next, n3)
        self.assertIs(n3.prev, n1)

    def test_delete_head_node(self):
        for v in [1, 2, 3]:
            self.list.insert(v)

        self.list.remove(1)
        with self.assertRaises(ValueError):
            _ = self.list.search(1)
        n2 = self.list.search(2)
        self.assertIs(n2.prev, self.list.nil)


    def test_delete_tail_node(self):
        for v in [1, 2, 3]:
            self.list.insert(v)

        self.list.remove(3)
        with self.assertRaises(ValueError):
            _ = self.list.search(3)
        
        n2 = self.list.search(2)
        self.assertIs(n2.next, self.list.nil)

    def test_delete_nonexistent_value(self):
        self.list.insert(1)
        self.list.insert(2)
        with self.assertRaises(ValueError):
            self.list.remove(999)  # Should not raise
        
        self.assertIsNotNone(self.list.search(1))
        self.assertIsNotNone(self.list.search(2))

    def test_insert_and_delete_until_empty(self):
        values = [5, 10, 15]
        for v in values:
            self.list.insert(v)

        for v in values:
            self.list.remove(v)

        for v in values:
            with self.assertRaises(ValueError):
                _ = self.list.search(v)

        # Depending on your implementation, you may check head is None
        self.assertIs(self.list.head, self.list.nil)
        self.assertTrue(self.list.empty())


if __name__ == "__main__":
    unittest.main()
