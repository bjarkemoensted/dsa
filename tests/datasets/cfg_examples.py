"""Defines a test dataset consisting of some CNFs and a couple of sentences for each grammar,
including a boolean indicating whether the sentences are members of the grammar"""

from dataclasses import dataclass

from dsa.algorithms.formal_languages.context_free import Nonterminal, productiontype


@dataclass
class Example:
    name: str
    productions: productiontype
    start_symbol: Nonterminal
    sentences: list[tuple[tuple[str, ...], bool]]


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
    (("a",), False),
    ((), True),
]

example_balanced = Example(
    name="balanced",
    productions=g_balanced,
    start_symbol=S,
    sentences=sentences_balanced
)


# B) Palindromes (non-CNF but CFG)
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

# C) Arithmetic Expressions
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


all_examples = (
    example_balanced,
    example_palindrome,
    example_arithmetic,
    example_empty
)


example_illegal = Example(
    name="deadend",
    start_symbol=S,
    productions={
        S: [
            (S, 'a', 'b', E)
        ]
    },
    sentences=[]
)