import unittest

from dsa.data_structures import heap_operations
from dsa.data_structures.heap import Heap

from ..utils import make_integers


class TestHeap(unittest.TestCase):
    min_heap = True
    
    def get_vals(self):
        return make_integers(n=100)
    
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
        vals = make_integers(n=100_000)
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
        self.vals = make_integers(n=1000)
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


class TestHeapClass(unittest.TestCase):
    def setUp(self):
        self.heap = Heap(values=make_integers(n=200))
        return super().setUp()
    
    def test_heap_property(self):
        self.assertTrue(self.heap._satisfies_heap_invariant())
    
    def test_push(self):
        n_items = len(self.heap)
        for val in make_integers(seed=1337):
            self.heap.push(val)
            self.assertTrue(self.heap._satisfies_heap_invariant())
            n_items += 1
            self.assertEqual(n_items, len(self.heap))
        #
    
    def test_pop(self):
        for _ in range(len(self.heap)):
            val = self.heap.pop()
            self.assertTrue(all(self.heap.comp(val, other) for other in self.heap.A))
            self.assertTrue(self.heap._satisfies_heap_invariant())
        #
        
        self.assertRaises(IndexError, self.heap.pop)
    #
    
    def test_height(self):
        for n in range(100):
            vals = range(n)
            depth_brute = 0
            ind = 0
            while ind < n:
                depth_brute += 1
                ind = heap_operations._left(ind)
                
            heap = Heap(vals)
            self.assertEqual(depth_brute, heap.height)
        #
    
    def test_ascii_representation(self):
        n_vals = [0, 1, 3, 4, 15, 31, 32, 1023]
        for n in n_vals:
            values = make_integers(n=n)
            heap = Heap(values)
            ascii = heap.ascii_tree()
            # Check that all lines have the same length in the ascii representation
            self.assertEqual(len({len(line) for line in ascii.splitlines()}), 1)
            
            if n != 0:
                # For non-empty heaps, check that all values on the heap appear in the tree
                recovered = [int(elem) for line in ascii.splitlines() for elem in line.strip().split()]
                self.assertEqual(sorted(recovered), sorted(values))
            #
        #
    #
