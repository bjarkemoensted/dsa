import unittest

from dsa.data_structures.linear.queue import Queue

from .linear_basic_tests import TestLinear


class BasicQueueTest(TestLinear):
    def create_data_structure(self, *args: object, **kwargs: object) -> Queue[int]:
        return Queue(*args, **kwargs)  # type: ignore


class QueueTest(unittest.TestCase):
    def setUp(self) -> None:
        self.unbounded_q: Queue[int] = Queue()
        self.bounded_q: Queue[str] = Queue(maxsize=3)

    def test_enqueue_unbounded(self) -> None:
        self.unbounded_q.enqueue(1)
        self.unbounded_q.enqueue(2)
        self.assertEqual(self.unbounded_q.size(), 2)
        self.assertFalse(self.unbounded_q.empty())
        self.assertFalse(self.unbounded_q.full())

    def test_enqueue_bounded(self) -> None:
        self.bounded_q.enqueue("a")
        self.bounded_q.enqueue("b")
        self.bounded_q.enqueue("c")
        self.assertEqual(self.bounded_q.size(), 3)
        self.assertTrue(self.bounded_q.full())
        with self.assertRaises(RuntimeError):
            self.bounded_q.enqueue("d")

    def test_dequeue(self) -> None:
        self.unbounded_q.enqueue(10)
        self.unbounded_q.enqueue(20)
        self.assertEqual(self.unbounded_q.dequeue(), 10)  # FIFO
        self.assertEqual(self.unbounded_q.dequeue(), 20)
        self.assertTrue(self.unbounded_q.empty())
        with self.assertRaises(RuntimeError):
            self.unbounded_q.dequeue()  # now empty

    def test_size(self) -> None:
        self.assertEqual(self.unbounded_q.size(), 0)
        for i in range(5):
            self.unbounded_q.enqueue(i)
        self.assertEqual(self.unbounded_q.size(), 5)
        self.unbounded_q.dequeue()
        self.assertEqual(self.unbounded_q.size(), 4)
