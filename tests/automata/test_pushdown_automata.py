import unittest
from collections.abc import Sequence

from dsa.automata import EMPTY_STACK, EPSILON, PDA, AutomatonBase
from dsa.utils import Sentinel

from ..datasets import cfg_examples

# Define the pushdown automaton of example 2.14 in Sipser, which recognizes {0^n 1^n | n >= 0}.
_pda_trans1: dict[tuple[str, int|Sentinel, int|Sentinel], set[tuple[str, int|Sentinel]]] = {
    ("q1", EPSILON, EPSILON): {("q2", EMPTY_STACK)},
    ("q2", 0, EPSILON): {("q2", 0)},
    ("q2", 1, 0): {("q3", EPSILON)},
    ("q3", 1, 0): {("q3", EPSILON)},
    ("q3", EPSILON, EMPTY_STACK): {("q4", EPSILON)}
}

pda1: PDA[str, int, int] = PDA(
    states={"q1", "q2", "q3", "q4"},
    alphabet={0, 1},
    initial_state="q1",
    final_states={"q1", "q4"},
    stack_alphabet={0},
    transitions=_pda_trans1,
)


cases: list[tuple[AutomatonBase, Sequence, bool]] = [
    (pda1, [], True),
    (pda1, [0, 1], True),
    (pda1, [0, 0, 1, 1], True),
    (pda1, [0, 0, 0, 1, 1, 1], True),

    # Wrong number of 0s and 1s
    (pda1, [0], False),
    (pda1, [1], False),
    (pda1, [0, 0, 1], False),
    (pda1, [0, 1, 1], False),
    (pda1, [0, 0, 0, 1, 1], False),

    # Wrong ordering
    (pda1, [1, 0], False),
    (pda1, [0, 1, 0, 1], False),
    (pda1, [0, 0, 1, 0, 1], False),
    (pda1, [1, 1, 0, 0], False),
]


class TestPDA(unittest.TestCase):
    def test_acceptance(self) -> None:
        for machine, input_, expected in cases:
            res = machine.accepts(input_)
            print(f"{input_}, {res} ?= {expected}")
            self.assertIs(res, expected)


_cfg_examples = (
    cfg_examples.example_balanced,
    cfg_examples.example_empty,
    cfg_examples.example_arithmetic,
    cfg_examples.example_palindrome
)


# !!!!!
# class TestCFGExamples(unittest.TestCase):
#     def test_pda_conversion(self) -> None:
#         for ex in cfg_examples.all_examples:
#             pda = pda_from_cfg(ex.grammar)
#             print(f"*** {ex.name} ***")
#             for sentence, producible in ex.sentences:
#                 print(sentence)
#                 accepted = pda.accepts(sentence)
                
#                 self.assertIs(accepted, producible)
