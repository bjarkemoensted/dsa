# DSA playground  <!-- omit in toc --> 

This is just a repo for playing around with various data structure/algorithm topics. I'll probably mainly use this to aid my understanding of topics I'm not comfortable with, by writing my own implementations, with no intention of completeness or efficiency.

As I mainly use this repo for self-study of various CS problems, I'll often refer to the literature I'm following. Often, this will be _Introduction to Algorithms_ by Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, and Clifford Stein, (CLRS for short).
- [Data structures](#data-structures)
  - [Stack](#stack)
  - [Queue](#queue)
  - [Heap](#heap)
  - [Priority Queue](#priority-queue)


## Data structures
A few elementary data structures have been implemented so far.
Some classes share functionality such as inserting and removing elements - these derive from a base class which has abstract methods with agnostic terminology `_put`, `_get`, and `_size`. These are private because public versions (`put`, `get`, `size`) implement class-agnostic checks, such as throwing errors if attempting to get an element from an empty container. Any future thread-safe behaviors can also be implemented here. Child classes define aliases for the aforementioned methods to conform with conventions, such as stacks using `push` and `pop` for `put` and `get`, respectively.

### Stack
Implementing stacks in python is a bit artifical since python lists have all the functionality of a stack. To mimic the dynamic memory allocation needed for implementing a stack from an array, values are stored in a list with some fixed initial size, which is then extended when more space is needed (unless `maxsize` is provided and exceeded).
The implementation closely follows CLRS, except it uses zero indexing.

**Example**:
```python
from dsa.data_structures import Stack

stack: Stack[int] = Stack()
stack.push(42)
val = stack.pop()
assert val == 42
```

### Queue
Like stacks, the queue implementation closely follows CLRS, except using zero-indexing. Like CLRS, the queue leaves one element as None to make it simpler to check for emptiness and fullness.  

**Example**:
```python
from dsa.data_structures import Queue

q: Queue[str] = Queue()
q.enqueue("foo")
q.enqueue("bar")
assert q.dequeue() == "foo"
```

### Heap
Heap operation are implemented in two different ways, as functions operating on a list, and as a class.

#### Heap functions <!-- omit in toc -->
The first closely follows CLRS, but uses a somewhat different naming convention. CLRS uses '(max)-heapify' for the operation which restores the heap property by moving elements in violation of the heap property down through the heap (by recursively swapping with the larger child node), until the property is restored.

Slightly confusing (at least to me), the algorithm for restoring the heap property in the 'opposite' direction (swapping violating nodes with their parents up through the heap) isn't given until the section on priority queues, as is named 'heap-increase-key'.
In addition, the builtin `heapq` library uses `heapify` to denote the action of turning an entire list into a heap (CLRS uses 'build-(max)-heap' for this).

Attempting a clearer notation, I use the following terminology for the methods aimed at restoring a heap property which might be violated at the input node:
* `_restore_down` assumes that nodes below the input already satisfy the heap property, and restores it by moving the value at the input node _down_ through the heap (swapping with the largest child node), until the property is restored.
* `_restore_up` assumes that nodes above the input node already satisfy the heap property, and restores it by moving the value _up_ through the heap, by exchanging with parent nodes, until the property is restored.

For consistency with the standard library, the function which turns a list into a heap is named `heapify`.

To avoid clashes between variable names and functionality when implementing min- and max-heaps, I generally avoid using the terms 'larger' and 'smaller' in the code, opting instead to use 'better', thinking of the heap property as declaring that parent nodes must be at least as 'good' as their children.
Again for consistency with `heapq`, I use min-heaps as default. Functions like `heapify` take an optional parameter `min_heap` which can be set to false to create a max-heap instead.
In addition, heap methods support an optional 'key' parameter. If provided, the heap property is maintained in the result of applying the key function to each element in the heap. The rationale for allowing both a key function and min/max heap functionality (rather than just using e.g. a key multiplying by minus 1 as the key) is that it becomes non-trivial to negate non-numeric orderings (like a tuple of strings).

**Example**:
```python
from dsa.data_structures.heap_operations import heapify, heappush, heappop

numbers = [1,2,3,4,5]
heapify(numbers)  # heapifies in-place
heappush(numbers, -1)
assert heappop(numbers) == -1


def order(x: int) -> tuple[bool, int]:
    """Turn integer x into a tuple where the first element indicates whether x is odd."""
    is_odd = bool(x % 2)
    return (is_odd, x)


heapify(numbers, key=order)
smallest_even = heappop(numbers, key=order)
assert smallest_even == 2
```

#### Heap class <!-- omit in toc -->
Constantly passing around key functions and parameters denoting whether a heap is a min/max heap becomes cumbersome and error prone.
The `Heap` class can be used to define these at instantiation, after which the push and pop methods on the instance automatically use the same key and heap type.


**Example**:

```python
from dsa.data_structures.heap import Heap


def order(x: int) -> tuple[bool, int]:
    return (x % 7 == 0, x)

# Explicit type hint (Heap[int]) isn't needed. Type is inferred from the first argument
heap = Heap(range(20), key=order, min_heap=False)

# Pop the largest value which is a multiple of 7
value = heap.pop()
assert value == 14
```

Heaps can also display themselves as ASCII art trees with the `.ascii_tree()` method.


### Priority Queue


**Example**:
```python
from dsa.data_structures import PriorityQueue


q: PriorityQueue[int] = PriorityQueue()

# tuples of values and priorities (low=more important)
elems = [
    (1, 4.3),
    (42, 0.1),
    (1337, 1)
]

for item, priority in elems:
    q.put(item, priority=priority)

most_important = q.get()
assert most_important == 42
```
