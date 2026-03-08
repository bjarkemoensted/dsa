# DSA playground  <!-- omit in toc --> 

This is just a repo for playing around with various data structure/algorithm topics. I'll probably mainly use this to aid my understanding of topics I'm not comfortable with, by writing my own implementations, with no intention of completeness or efficiency.

As I mainly use this repo for self-study of various CS problems, I'll often refer to the literature I'm following. Often, this will be _Introduction to Algorithms_ by Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, and Clifford Stein, (CLRS for short).
- [Data structures](#data-structures)
  - [Stack](#stack)
  - [Queue](#queue)
  - [Heap](#heap)
  - [Priority Queue](#priority-queue)
  - [Linked List](#linked-list)
- [Algorithms](#algorithms)
  - [Context-free grammars](#context-free-grammars)
    - [CYK algorithm and parse trees](#cyk-algorithm-and-parse-trees)

# Data structures
A few elementary data structures have been implemented so far.
Some classes share functionality such as inserting and removing elements - these derive from a base class which has abstract methods with agnostic terminology `_put`, `_get`, and `_size`. These are private because public versions (`put`, `get`, `size`) implement class-agnostic checks, such as throwing errors if attempting to get an element from an empty container. Any future thread-safe behaviors can also be implemented here. Child classes define aliases for the aforementioned methods to conform with conventions, such as stacks using `push` and `pop` for `put` and `get`, respectively.

## Stack
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

## Queue
Like stacks, the queue implementation closely follows CLRS, except using zero-indexing. Like CLRS, the queue leaves one element as None to make it simpler to check for emptiness and fullness.  

**Example**:
```python
from dsa.data_structures import Queue

q: Queue[str] = Queue()
q.enqueue("foo")
q.enqueue("bar")
assert q.dequeue() == "foo"
```

## Heap
Heap operation are implemented in two different ways, as functions operating on a list, and as a class.

### Heap functions <!-- omit in toc -->
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

### Heap class <!-- omit in toc -->
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


## Priority Queue
The priority queue is implemented using [heap operations](#heap) to insert an element with a specified priority (with lower priorities corresponding to more important elements).
Oftentimes, simple implementations use tuples of an element's priority, and the element itself, in the underlying heap structure, because tuples are ordered in a recursive manner by the order of each or their elements.
The issue with this is that the queued elements will then be compared against each other in cases where 2 elements have the same priorities. If the queue is used with instances of a class that doesn't support comparison operations, an error will be raised.

The `PriorityQueue` implementation also stores tuples in its underlying heap, but uses compares them using a key function which only looks up the priority, avoiding using the queued elements as tiebreakers.

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

## Linked List
Linked lists are implemented using a `Node` class which stores an element in the list, and pointers to the next and previous nodes.
A sentinel node `nil` is used to represent the end of the list and point (via its `.next` and `.prev` attributes) to the head and tail of the list.

The implementation uses naming similar to that of the `collections.deque` class, so methods like `appendleft` and `popleft` are available in addition to `append` and `pop`, for modifying the left end of a linked list.


**Example**:
```python
from dsa.data_structures import LinkedList


q: LinkedList[int] = LinkedList(range(5))

last = q.pop()
assert last == 4

first = q.popleft()
assert first == 0
```

# Algorithms

## Context-free grammars
On the topic of formal languages, I will typically use Hopcroft, Motwani, and Ullman (HMU) as a reference:
> John E. Hopcroft, Rajeev Motwani, Jeffrey D. Ullman - Introduction to automata theory, languages, and computation, 3rd edition (2006).

I'll also refer to Michael Sipser (Sipser):
> Sipser M. *Introduction to the Theory of Computation*, 3rd edition (2012)

Some resources use terminology slightly different, so here's a brief overview of the terms used here, and some implementation details:


| Term | Description | Data type | Example |
|-----|-----|-----|-----|
| Nonterminal | A grammar symbol that can be expanded using production rules. Represented by upper-case letters | `Nonterminal` class | `S` |
| Terminal | A symbol that appears in the final output and cannot be expanded further. | `str` | `a` |
| Symbol | Either a terminal or a nonterminal. | `str\|Nonterminal` | `a` or `S` |
| Sentence | A sequence of terminals produced by the grammar. | `tuple[str, ...]` | `abc` |
| Empty string | Special case of a 'non-string', for e.g. a nonterminal producing nothing | empty tuple `()` | `ε` |
| Sentential form | A sequence of terminals/nonterminals. | `tuple[str\|Nonterminal]` | `aSb` |
| Production rules | Rules for how Nonterminals may be expanded. | `dict[Nonterminal, list[tuple[str\|Nonterminal, ...]]]` | `S → aS \| S \| ε` |
| Head / LHS | The nonterminal being expanded in a production. | `Nonterminal` | `S` in `S → aS \| S \| ε` |
| RHS/body/production | One individual sententials produced by a nonterminal | `tuple[str \| Nonterminal, ...]` | `aS` in `S → aS \| S \| ε` |

Context free grammars are implemented in the `CFG` class, and can be instantiated with a set of prodution rules, and a starting symbol. Grammars expose helpers methods for producing a random sentence/string, and for using breadth-first generation to brute force every possible sentence up to a given length:

```python
from dsa.formal_languages import (
    CFG,
    Nonterminal,
    productiontype  # alias for dict[Nonterminal, list[sententialtype]]
)


S = Nonterminal("S")

production_rules: productiontype = {
    S: [("a",), ("a", S), ("a", "b"), ()]
}

G = CFG(production_rules, S)

print(G.ascii)  # S → ('a',) | ('a', S) | ('a', 'b') | ε

s = G.random_string()
print(s)  # a

sentence = G.random_sentence()
print(sentence)  # ('a', 'b')

brute = G.brute_force_sentences(max_tokens=2)
print(brute)  # {('a', 'b'), (), ('a', 'a'), ('a',)}
```

There are subtly different definitions of CNF in the litterature, with differences in e.g. whether to consider empty strings as allowed.
I follow Sipser in including empty string productions from the start symbol, and also HMU in requiring the absence of 'useless symbols' (nonterminals which do not occur in any derivation).

Functionality for converting a grammar to Chomsky Normal Form (CNF) is also available.


<!--pytest-codeblocks:cont-->
```python
from dsa.formal_languages import chomsky_normal_form, grammar_is_cnf

assert not grammar_is_cnf(G)

G_cnf = chomsky_normal_form(G)
assert grammar_is_cnf(G_cnf)

```

### CYK algorithm and parse trees
The CYK algorithm is a dynamic programming algorithm, can efficiently determine whether a sentence a context-free grammar in Chomsky Normal Form implemented in the `CYKParser` class.

When a parser is initialized, it automatically converts is grammar to CNF and stores it.
Afterwarts, it can determine whether its grammar accepts a given sentence via the `.accept(sentence)` method, e.g. `parser.accepts(('a', 'b', 'a'))`.

A parse tree can be obtained by the `.parse` method, returning the root node of a parse tree (or `None`, is the sentence is not accepted). It's also possible to obtain every possible parse tree, in case the grammar is ambiguous (has multiple ways of deriving a sentence). This can be done using the `.make_parse_forest` method, which returns a `ParseForest` instance. If the sentence is not accepted, the forest is empty, and contains no trees. The `ParseForest` class supports iteration over the trees it encodes, e.g. `for tree in parse_forest: ...`.

```python
from dsa.formal_languages import (
    CFG,
    CYKParser,
    Nonterminal,
    productiontype
)


# Create an ambiguous grammar
S = Nonterminal("S")
g: productiontype = {
    S: [
        (S, S),
        ("a",),
    ]
}

# Make a parser for the grammar
G = CFG(g, S)
parser = CYKParser(G)

# Verify that the grammar accepts the sentence
sentence = ('a', 'a', 'a')
assert parser.accepts(sentence)

# Get a parse tree
parse_tree = parser.parse(sentence)
assert parse_tree is not None
# Verify that it produces the
assert parse_tree.sentence() == sentence

# Iterate over all possible parse trees
forest = parser.make_parse_forest(sentence)
for tree in forest:
    assert tree.sentence() == sentence
```

Parse trees represent how a grammar can derive a sentence, via repeated expansion of the grammar's nonterminals.
Each node in the tree holds a single symbol,
Non-leaf nodes hold nonterminal symbols, and their children hold each of the symbols into which the nonterminal is expanded in the derivation represented by the tree.
Leaf nodes always store string symbols, or nonterminals which generate the empty string ε.

Continuing the prior example, we can display the sequence of steps for deriving the sentence with the `.derivation` method of the root node.
The parse tree supports leftmost or rightmost derivations, i.e. repeated expansion of the leftmost or rightmost nonterminal:

<!--pytest-codeblocks:cont-->
```python

s1 = parse_tree.derivation()
assert s1 == "(S_1,) => (S, S) => ('a', S) => ('a', S, S) => ('a', 'a', S) => ('a', 'a', 'a')"

# Optionally, expand the rightmost symbols instead
s2 = parse_tree.derivation(direction="rightmost")
assert s2 == "(S_1,) => (S, S) => (S, S, S) => (S, S, 'a') => (S, 'a', 'a') => ('a', 'a', 'a')"
```

<!--pytest-codeblocks:cont-->
```python

s1 = parse_tree.derivation()
assert s1 == "(S_1,) => (S, S) => ('a', S) => ('a', S, S) => ('a', 'a', S) => ('a', 'a', 'a')"

# Optionally, expand the rightmost symbols instead
s2 = parse_tree.derivation(direction="rightmost")
assert s2 == "(S_1,) => (S, S) => (S, S, S) => (S, S, 'a') => (S, 'a', 'a') => ('a', 'a', 'a')"
```

An ASCII-representation of a parse tree can also be obtained with `parse_tree.ascii_tree()`, which gives the following string:
```
S_1
├── S
│   └── 'a'
└── S
    ├── S
    │   └── 'a'
    └── S
        └── 'a'
```
