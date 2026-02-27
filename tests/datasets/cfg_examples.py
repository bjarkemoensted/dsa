"""Defines a test dataset consisting of some CNFs and a couple of sentences for each grammar,
including a boolean indicating whether the sentences are members of the grammar"""

from dataclasses import dataclass

from dsa.algorithms.formal_languages.context_free import (
    Grammar,
    productiontype
)
from dsa.algorithms.formal_languages.types import Nonterminal


@dataclass
class Example:
    """Container for example data. To collect example grammars and some sentences
    to make testing simpler."""

    name: str
    productions: productiontype
    start_symbol: Nonterminal
    sentences: list[tuple[tuple[str, ...], bool]]

    @property
    def grammar(self) -> Grammar:
        G = Grammar(production_rules=self.productions, start_symbol=self.start_symbol)
        return G
    #

### 'balanced' grammar producing a^n b^n,  e.g. "", "ab", "aabb", etc
S = Nonterminal("S")

g_balanced = {
    S: [
        ("a", S, "b"),
        (),  # epsilon
    ]
}

sentences_balanced = [
    (("a", "b"), True),
    (("a", "a", "b", "b"), True),
    (("a", "b", "a", "b"), False),
    (("a", "a", "a", "b", "b", "b"), True),
    (("a",), False),
    ((), True),
]


example_balanced = Example(
    name="balanced",
    productions=g_balanced,
    start_symbol=S,
    sentences=sentences_balanced
)

### CNF version of balanced grammar, producing e.g. "ab", "aabb", etc (no empty string now)

X = Nonterminal("X")
A = Nonterminal("A")
B = Nonterminal("B")


g_balanced_cnf: productiontype = {
    S: [
        (A, X),
        (A, B),
        (),
    ],
    X: [
        (S, B),
    ],
    A: [
        ("a",),
    ],
    B: [
        ("b",),
    ],
}


example_balanced_cnf = Example(
    name="balanced_cnf",
    productions=g_balanced_cnf,
    start_symbol=S,
    sentences=sentences_balanced
)

### Example grammar for palindromes

S2 = Nonterminal("S2")

g_palindrome = {
    S2: [
        ("a", S2, "a"),
        ("b", S2, "b"),
        ("a",),
        ("b",),
        (),  # epsilon
    ]
}

sentences_palindrome = [
    ((), True),
    (("a",), True),
    (("b",), True),
    (("a", "a"), True),
    (("b", "b"), True),
    (("a", "b", "a"), True),
    (("b", "a", "b"), True),
    (("a", "b"), False),
    (("a", "a", "b"), False),
    (("b", "a", "a", "b"), False),
]

example_palindrome = Example(
    name="palindrome",
    productions=g_palindrome,
    start_symbol=S2,
    sentences=sentences_palindrome
)

### Example grammar for arithmetic expressions

E = Nonterminal("E")
T = Nonterminal("T")
F = Nonterminal("F")

g_arith = {
    E: [
        (E, "+", T),
        (T,),
    ],
    T: [
        (T, "*", F),
        (F,),
    ],
    F: [
        ("(", E, ")"),
        ("id",),
    ],
}

sentences_arith = [
    (("id",), True),
    (("id", "+", "id"), True),
    (("id", "+", "id", "*", "id"), True),
    (("(", "id", "+", "id", ")", "*", "id"), True),
    (("id", "*"), False),
    (("+", "id"), False),
    (("id", "*", "(", "id", "+", "id"), False),
]

example_arithmetic = Example(
    name="arithmetic",
    productions=g_arith,
    start_symbol=E,
    sentences=sentences_arith
)

### Example 'empty' grammar, which only produces the empty string (for testing edge cases etc)

S3 = Nonterminal("S3")

g_empty: productiontype = {
    S3: [()]
}

sentences_empty = [
    ((), True),
    (("a", "a"), False),
    (("(", ")"), False),
    (("",), False),
]

example_empty = Example(
    name="empty",
    productions=g_empty,
    start_symbol=S3,
    sentences=sentences_empty
)

# Combining some examples of grammars for testing

all_examples = (
    example_balanced,
    example_balanced_cnf,
    example_palindrome,
    example_arithmetic,
    example_empty
)

### Example of an 'illegal' grammar, where a nonterminal has no productions.

example_illegal = Example(
    name="deadend",
    start_symbol=S,
    productions={
        S: [
            (E, 'a', 'b', S)
        ]
    },
    sentences=[]
)

### Example of a grammar with 'useless' symbols - a nonterminal is unreachable

example_useless = Example(
    name="useless",
    start_symbol=S,
    productions={
        S: [(S, 'a', 'b')],
        E: [(S, 'b', 'c')]
    },
    sentences=[]
)
