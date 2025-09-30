import unittest

from dsa.data_structures.linear import PriorityQueue

from .linear_basic_tests import TestLinear


class BasicPriorityQueueTest(TestLinear):
    def create_data_structure(self, *args, **kwargs) -> PriorityQueue[int]:
        return PriorityQueue(*args, **kwargs)
    #


class _CustomObject:
    """A custom class which doesn't support comparison.
    This is to test that priority queues operate only on the priority itself, without
    relying on queued objects for tie breaking."""
    pass


class TestPriorityQueue(unittest.TestCase):

    def setUp(self):
        self.q = PriorityQueue()

    def test_put_and_get_single_element(self):
        self.q.put("task1", priority=1)
        self.assertEqual(self.q.get(), "task1")

    def test_put_and_get_multiple_elements(self):
        self.q.put("low", priority=5)
        self.q.put("high", priority=1)  # assuming lower number = higher priority
        self.q.put("medium", priority=3)
        self.assertEqual(self.q.get(), "high")
        self.assertEqual(self.q.get(), "medium")
        self.assertEqual(self.q.get(), "low")

    def test_stability_with_same_priority(self):
        self.q.put("task1", priority=2)
        self.q.put("task2", priority=2)
        self.q.put("task3", priority=2)
        # If stable, order should be FIFO for equal priorities
        self.assertEqual(self.q.get(), "task1")
        self.assertEqual(self.q.get(), "task2")
        self.assertEqual(self.q.get(), "task3")

    def test_mixed_priorities_and_order(self):
        self.q.put("a", priority=10)
        self.q.put("b", priority=1)
        self.q.put("c", priority=5)
        self.q.put("d", priority=1)
        # "b" and "d" both priority=1; "b" should come first if stable
        self.assertEqual(self.q.get(), "b")
        self.assertEqual(self.q.get(), "d")
        self.assertEqual(self.q.get(), "c")
        self.assertEqual(self.q.get(), "a")

    def test_large_number_of_elements(self):
        for i in range(1000):
            self.q.put(f"item{i}", priority=i)
        self.assertEqual(self.q.get(), "item0")  # smallest priority first
    #

    def test_custom_objects(self):
        items = [_CustomObject() for _ in range(3)]
        for item in items:
            self.q.put(item, priority=1)
        
        recovered = []
        while self.q.size() > 0:
            recovered.append(self.q.get())
        
        self.assertEqual(len(recovered), len(items))