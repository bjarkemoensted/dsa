import unittest

from dsa.data_structures.linear.priority_queue import PriorityQueue

from .linear_basic_tests import TestLinear


class BasicPriorityQueueTest(TestLinear):
    @staticmethod
    def get(container: PriorityQueue[int]) -> int:
        return container.pop()

    @staticmethod
    def put(container: PriorityQueue[int], item: int) -> None:
        return container.push(item, priority=1)
    
    def create_data_structure(self, *args: object, **kwargs: object) -> PriorityQueue[int]:
        return PriorityQueue(*args, **kwargs)  # type: ignore


class _CustomObject:
    """A custom class which doesn't support comparison.
    This is to test that priority queues operate only on the priority itself, without
    relying on queued objects for tie breaking."""


class TestPriorityQueue(unittest.TestCase):

    def setUp(self) -> None:
        self.q: PriorityQueue[str] = PriorityQueue()

    def test_put_and_get_single_element(self) -> None:
        self.q.push("task1", priority=1)
        self.assertEqual(self.q.pop(), "task1")

    def test_put_and_get_multiple_elements(self) -> None:
        self.q.push("low", priority=5)
        self.q.push("high", priority=1)  # assuming lower number = higher priority
        self.q.push("medium", priority=3)
        self.assertEqual(self.q.pop(), "high")
        self.assertEqual(self.q.pop(), "medium")
        self.assertEqual(self.q.pop(), "low")

    def test_stability_with_same_priority(self) -> None:
        self.q.push("task1", priority=2)
        self.q.push("task2", priority=2)
        self.q.push("task3", priority=2)
        # If stable, order should be FIFO for equal priorities
        self.assertEqual(self.q.pop(), "task1")
        self.assertEqual(self.q.pop(), "task2")
        self.assertEqual(self.q.pop(), "task3")

    def test_mixed_priorities_and_order(self) -> None:
        self.q.push("a", priority=10)
        self.q.push("b", priority=1)
        self.q.push("c", priority=5)
        self.q.push("d", priority=1)
        # "b" and "d" both priority=1; "b" should come first if stable
        self.assertEqual(self.q.pop(), "b")
        self.assertEqual(self.q.pop(), "d")
        self.assertEqual(self.q.pop(), "c")
        self.assertEqual(self.q.pop(), "a")

    def test_large_number_of_elements(self) -> None:
        for i in range(1000):
            self.q.push(f"item{i}", priority=i)
        self.assertEqual(self.q.pop(), "item0")  # smallest priority first

    def test_custom_objects(self) -> None:
        q: PriorityQueue[_CustomObject] = PriorityQueue()
        items = [_CustomObject() for _ in range(3)]
        for item in items:
            q.push(item, priority=1)
        
        recovered = []
        while q.size() > 0:
            recovered.append(q.pop())
        
        self.assertEqual(len(recovered), len(items))
