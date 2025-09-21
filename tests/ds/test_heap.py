import random
import unittest

from dsa.data_structures import heap_operations


def get_vals(n: int=100, seed=42, low=-100, high=100):
        rs = random.Random()
        rs.seed(seed)
        res = [rs.randint(low, high) for _ in range(n)]
        return res
    #


class TestHeap(unittest.TestCase):
    min_heap = True
    
    def get_vals(self):
        return get_vals(n=100)
    
    def setUp(self):
        self.vals = self.get_vals()
        self.vals_heap = [v for v in self.vals]
        heap_operations.heapify(self.vals_heap, min_heap=self.min_heap)
    
    def heap_property_satisfied(self, vals) -> bool:
        res = heap_operations._satisfies_heap_property(vals, min_heap=self.min_heap)
        return res
    
    def test_satisfy_heap_prop_function(self):
        """Check the function for determining whether the heap property is satisfied"""
        
        # Check positive case
        self.assertTrue(self.heap_property_satisfied(self.vals_heap))

        # Check that permuting non-identical parent-child pairs causes the property to be violated
        for i1, i2 in heap_operations.iterate_parent_child_pairs(size=len(self.vals_heap)):
            vals = [v for v in self.vals_heap]
            parent = vals[i1]
            child = vals[i2]
            if parent == child:
                continue
            
            vals[i1], vals[i2] = vals[i2], vals[i1]
            still_heap = self.heap_property_satisfied(vals)
            self.assertFalse(still_heap)
        #
    
    def test_heapify(self):
        heap_operations.heapify(self.vals, min_heap=self.min_heap)
        satisfies_heap_prop = self.heap_property_satisfied(self.vals)
        self.assertTrue(satisfies_heap_prop)

    def test_insert(self):
        heap_operations.heapify(self.vals, min_heap=self.min_heap)
        new_values = self.get_vals()
        for val in new_values:
            self.assertTrue(self.heap_property_satisfied(self.vals))
            heap_operations.heappush(self.vals, val, min_heap=self.min_heap)
        #

    def test_remove(self):
        for _ in range(len(self.vals_heap)):
            # Check that heap proprty persist after popping an element
            heap_operations.heappop(self.vals_heap, min_heap=self.min_heap)
            self.assertTrue(self.heap_property_satisfied(self.vals_heap))
        #
    
    def test_large_heap(self):
        vals = get_vals(n=100_000)
        heap_operations.heapify(vals, min_heap=self.min_heap)
        good = self.heap_property_satisfied(vals)
        self.assertTrue(good)
    #


class TestMaxHeap(TestHeap):
    min_heap = False
    
    def test_ordering(self):
        """Double check that the ordering between parent and child nodes is parent >= child"""
        for ip, ic in heap_operations.iterate_parent_child_pairs(size=len(self.vals_heap)):
            self.assertGreaterEqual(self.vals_heap[ip], self.vals_heap[ic])
        #
    #


class TestSorting(unittest.TestCase):
    def setUp(self):
        self.vals = get_vals(n=1000)
        return super().setUp()
    
    def test_heap_sort(self):
        heap_operations.heapsort(self.vals)
        for i in range(len(self.vals) - 1):
            i2 = i+1
            a = self.vals[i]
            b = self.vals[i2]
            self.assertTrue(
                a <= b,
                f"Subsequent elements out of order at index {i} (values {a}, {b})"
            )
        #
    #
