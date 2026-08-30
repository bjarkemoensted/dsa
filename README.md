# DSA playground  <!-- omit in toc --> 

This is just a repo for playing around with various data structure/algorithm topics. I'll probably mainly use this to aid my understanding of topics I'm not comfortable with, by writing my own implementations, with no intention of completeness or efficiency.

As I mainly use this repo for self-study of various CS problems, I'll often refer to the literature I'm following. Often, this will be _Introduction to Algorithms_ by Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, and Clifford Stein, (CLRS for short).
- [Data structures](#data-structures)
  - [Stack](#stack)
  - [Queue](#queue)
  - [Heap](#heap)
  - [Priority Queue](#priority-queue)
  - [Linked List](#linked-list)
- [Automata \& Formal Languages](#automata--formal-languages)
  - [Regular languages \& Finite State Automata](#regular-languages--finite-state-automata)
    - [Finite State Automata](#finite-state-automata)
    - [Regular Expressions](#regular-expressions)
  - [Context-free grammars \& Pushdown Automata](#context-free-grammars--pushdown-automata)
    - [Context-Free Grammars (CFGs)](#context-free-grammars-cfgs)
      - [CYK algorithm and parse trees](#cyk-algorithm-and-parse-trees)
    - [Pushdown Automata](#pushdown-automata)

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

# Automata & Formal Languages
This section concerns formal language theory, along with the associated automata theory.

This subject is pretty tricky (to me anyways), and sources occationally differ slightly in how they do things.
I refer to multiple books for that reason, depending on the exact topic, because one book might explain one topic well, and skip over another.

Some basic terminology:

| Term | Description |
|-----|-----|
| State | An allowed state in an automaton. Often represented as nodes in a graph (with edges representing state transitions) |
| Alphabet | The set of allowed characters in the input to an automaton. For example, an automaton might recognize strings like 'ab', 'aab', 'aaab', etc., and have alphabet `{'a', 'b'}` |
| Initial state| The state in which an automaton begins its processing of a string. An initial state is often depicted with an ingoing arrow. For instance, if the initial state is `0`, it might be shown as ` -> 0` |
| Final state | Also called *accept state* in some sources. If an automata ends in one the final states after processing a string, the string is *accepted* by the automaton. Final states are often circled in depection, e.g. `(0)` |
| Transitions | Also called 'transition function' or 'transition rules'. Given a state and a single input token (possible an empty string in some cases), the transition function determines which subsequent states are reachable. Formally, the transition function maps the Cartesian product of states and alphabet onto the states, e.g. it maps any possible combination of one state and one character in the alphabet to a new state. For simplicity, I implement this as a dictionary, not necessary including all state-character combinations among the keys. If an automaton encounters a combination which is absent in the transition dictionary, it will reject the string being processed. This is equivalent to mapping each such combination to some terminal state from which escape is impossible, and so doesn't fundamentally change anything. Transitions are often depicted as arrows, with the character above or on the arrow. For example, `0 -a-> 1` might indicate that the `0` can transition to the `1` state, by consuming the character 'a'.|
| Empty string | An empty stirng containing no characters. Often represented as epsilon "ε". A transition with an empty string means the transition is allowed without consuming from the input |
| accept / reject| An automaton can accept or reject a string. For example, the automaton ->  `-> 0 -a-> 1 --b-ε-> (2)` accepts strings  'ab' (by consuming first a and then b), and 'a' (by consuming first a, then the empty string), and rejects all other strings |
| Language | The set of all strings accepted by an automaton. We say that an automaton *recognizes* the language made up of all the strings it accepts |


## Regular languages & Finite State Automata
An automaton is a simple state machine which holds a number of allowed states, and rules for transitioning between states when tokens are consumed from an input.
Automata can *accept* or *reject* an input, meaning determine whether the input matches some pattern defined by the automaton.
On the topic of automata, I mainly refer to Michael Sipser (Sipser):
> Sipser M. *Introduction to the Theory of Computation*, 3rd edition (2012)

### Finite State Automata
Automata are implemented as simple dataclasses.
Deterministic finite automata (DFAs) can be instantiated, and used to match strings, as shown in the following example:

```python
from dsa.automata import DFA


t: dict[tuple[int, str], int] = {
    (0, "a"): 1,  # even number of 'a' seen
    (1, "a"): 0,  # odd number of 'a' seen
    (1, "b"): 2,  # accept if we get 'b' after odd N a
}

dfa = DFA(
    initial_state=0,
    final_states={2,},
    transitions=t,
    states={0, 1, 2},
    alphabet={'a', 'b'}
)

good_strings = ("ab", "aaab")
bad_strings = ("b", "aab")

assert all(dfa.accepts(s) for s in good_strings)
assert all(not dfa.accepts(s) for s in bad_strings)
```

Non-determininistic finite automata (NFAs) are similar, except 1) they allow multiple target nodes given a single source node and input token combination, and 2) they allow 'epsilon transitions', meaning transitions from one state to another, without consuming input.

To keep the machinery for NFAs agnostic as to the type of their inputs, the empty string is represented by a singleton `EPSILON`. This is to avoid complications if one were to use e.g. `''` or `None` as valid characters in an alphabet.

An NFA can be instantiated in exactly the same way, except the transition dict now to a set of target nodes, rather than a single node.

<!--pytest-codeblocks:cont-->
```python
from dsa.automata import NFA

nfa = NFA(
    initial_state=0,
    final_states={2,},
    transitions={k: {v,} for k, v in t.items()},  # use a set of target states this time
    states={0, 1, 2},
    alphabet={'a', 'b'}
)

assert all(nfa.accepts(s) for s in good_strings)
assert all(not nfa.accepts(s) for s in bad_strings)

```

It can be shown that DFA's and NFA's are equivalent, meaning any NFA can be converted into a DFA which recognizes the same language, and vice versa.

The term 'regular language' refers to any language (set of strings) recognized by a finite state automaton. For example, the simple automata from the previous code snippets define the language `{'ab', 'aaab', 'aaaaab', ...}`

### Regular Expressions
A regular expression is a small pattern which can be compared against strings. For example `"aab*"` means "the character 'a' twice, followed by the character 'b' repeated zero or more times". Some special characters in regular expressions:

* `|` - union. For example `'a|b'` represents 'a' or 'b'.
* `*` - Kleene star. For example `'a*'` means 'a' repeated zero or more times.
* `()` - Parentheses. Used to override order of operations. For example,  `aa|b` means either 'aa' or 'b', whereas `a(a|b)` means 'a' followed by 'a' or 'b' (matching 'aa' or 'ab').

Any well-formed regular expression can be converted into an NFA, and thus corresponds to a regular language.

The conversion from a regular expression into an NFA follows section 2.7 in *Cooper and Torczon*:
> Cooper, Keith D., Linda Torczon. *Engineering a compiler*, 2004.

The approach uses *Thompson's construction*, breaking a regular expression into smaller components, turning each into a small fragment of an NFA, then combining them using various rules. For example, 2 fragments F1 and F2, which accept 'a', and 'b', respectively, can be combined into a single fragment which accepts 'ab' using an epsilon transition from the final state of F1 to the initial state of F2.
The fragments are obtained by parsing the expression using the shunting yard algorithm, to construct an abstract syntax tree (AST) representing the literal parts of the expression (e.g. 'a', 'b'), and operators (e.g. '|').

The conversion from a regular expression into a corresponding NFA can be donw as whoen in the following.

```python
from dsa.automata.regex import regex_to_NFA


nfa = regex_to_NFA("a(a|b)*")

assert nfa.accepts("a")
assert nfa.accepts("abba")
assert not nfa.accepts("")
assert not nfa.accepts("baab")
```


## Context-free grammars & Pushdown Automata
On the topic of formal languages, I will typically use Hopcroft, Motwani, and Ullman (HMU) as a reference:
> John E. Hopcroft, Rajeev Motwani, Jeffrey D. Ullman - Introduction to automata theory, languages, and computation, 3rd edition (2006).


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

### Context-Free Grammars (CFGs) 
Context free grammars are implemented in the `CFG` class, and can be instantiated with a set of prodution rules, and a starting symbol. Grammars expose helpers methods for producing a random sentence/string, and for using breadth-first generation to brute force every possible sentence up to a given length:

```python
from dsa.formal_languages import (
    CFG,
    Nonterminal,
    ProductionType  # alias for dict[Nonterminal, list[sententialtype]]
)


S = Nonterminal("S")

production_rules: ProductionType = {
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

#### CYK algorithm and parse trees
The CYK algorithm is a dynamic programming algorithm, can efficiently determine whether a sentence a context-free grammar in Chomsky Normal Form implemented in the `CYKParser` class.

When a parser is initialized, it automatically converts is grammar to CNF and stores it.
Afterwarts, it can determine whether its grammar accepts a given sentence via the `.accept(sentence)` method, e.g. `parser.accepts(('a', 'b', 'a'))`.

A parse tree can be obtained by the `.parse` method, returning the root node of a parse tree (or `None`, is the sentence is not accepted). It's also possible to obtain every possible parse tree, in case the grammar is ambiguous (has multiple ways of deriving a sentence). This can be done using the `.make_parse_forest` method, which returns a `ParseForest` instance. If the sentence is not accepted, the forest is empty, and contains no trees. The `ParseForest` class supports iteration over the trees it encodes, e.g. `for tree in parse_forest: ...`.

```python
from dsa.formal_languages import (
    CFG,
    CYKParser,
    Nonterminal,
    ProductionType
)


# Create an ambiguous grammar
S = Nonterminal("S")
g: ProductionType = {
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

### Pushdown Automata
Just as regular languages are defined as being recognized by a finite state automaton, context-free languages are defined as being recognized a pushdown automaton.
TODO: Get into pushdown automata.