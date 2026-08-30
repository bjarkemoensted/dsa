import unittest
from collections.abc import Sequence
from itertools import product

from dsa.automata.finite_state_machine import DFA, EPSILON, NFA, AutomatonBase

dfa_kwargs_1 = {
    "states": {"q1", "q2"},
    "alphabet": {0, 1},
    "transitions": {
        ("q1", 0): "q1",
        ("q1", 1): "q2",
        ("q2", 0): "q1",
        ("q2", 1): "q2",
    },
    "initial_state": "q1",
    "final_states": {"q2"},
}

dfa1: DFA[str, int] = DFA(**dfa_kwargs_1) #  type: ignore

kwargs = dfa_kwargs_1.copy()
transitions = dfa_kwargs_1["transitions"]
assert isinstance(transitions, dict)
nfa_equivalent: NFA[str, int] = NFA(
    **(dfa_kwargs_1 | {"transitions": {k: {v,} for k, v in transitions.items()}})  # type: ignore
)

cases: list[tuple[AutomatonBase, Sequence, bool]] = [
    # Example 1.7 in Sipser
    (dfa1, [1, 1, 0, 1], True),
    (dfa1, [1, 1, 0], False),
    (nfa_equivalent, [1, 1, 0, 1], True),
    (nfa_equivalent, [1, 1, 0], False),
]


class TestDFA(unittest.TestCase):
    def test_acceptance(self) -> None:
        for machine, string, valid in cases:
            accepted = machine.accepts(string)
            self.assertIs(accepted, valid)
    
    def test_invalid_machine_raises_error(self) -> None:
        invalid_kwargs = [
            {"final_states": {"x",}},
            {"initial_state": 99}
        ]

        for d in invalid_kwargs:
            with self.assertRaises(RuntimeError):
                DFA(**(dfa_kwargs_1 | d))  # type: ignore
    
    def test_nfa_acceptance(self) -> None:
        """Check that an NFA whivc gives sets of single states accepts the same
        strings as the same DFA"""

        kwargs = dfa_kwargs_1.copy()
        transitions = kwargs["transitions"]
        assert isinstance(transitions, dict)
        kwargs["transitions"] = {k: {v,} for k, v in transitions.items()}

        for machine, string, valid in cases:
            accepted = machine.accepts(string)
            self.assertIs(accepted, valid)


# NFA N1 (example 1.38 in Sipser) - accepts strings w. 101 or 11 as a substring
nfa_kwargs_1 = {
    "states": {"q1", "q2", "q3", "q4"},
    "alphabet": {0, 1},
    "transitions": {
        ("q1", 0): {"q1",},
        ("q1", 1): {"q1", "q2"},
        ("q2", 0): {"q3",},
        ("q2", EPSILON): {"q3",},
        ("q3", 1): {"q4",},
        ("q4", 0): {"q4",},
        ("q4", 1): {"q4",},
    },
    "initial_state": "q1",
    "final_states": {"q4",},
}


def _is_sub_tuple[T](a: tuple[T, ...], b: tuple[T, ...]) -> bool:
    """Determines whether a is a sub tuple of b"""
    for i in range(len(b)):
        j = i + len(a)
        if j > len(b):
            break
        snippet = b[i:j]
        if a == snippet:
            return True

    return False


NFA1 = NFA(**nfa_kwargs_1)  # type: ignore

nfa1_cases = (
    (elem, any(_is_sub_tuple(pattern, elem) for pattern in ((1, 0, 1), (1, 1))) )
    for n in range(6) for elem in product([0, 1], repeat=n)
)


class TestNFA(unittest.TestCase):
    def test_nfa_1(self) -> None:
        for string, match in nfa1_cases:
            machine_match = NFA1.accepts(string)
            self.assertIs(match, machine_match, f"Error with string {string}. Expected {match}, got {machine_match}")

    def test_nfa_4(self) -> None:
        """Checks example 1.35 in Sipser"""
        nfa = NFA(
            states={"q1", "q2", "q3"},
            initial_state="q1",
            alphabet={"a", "b"},
            final_states={"q1",},
            transitions={
                ("q1", "b"): {"q2",},
                ("q1", EPSILON): {"q3",},
                ("q2", "a"): {"q2", "q3"},
                ("q2", "b"): {"q3",},
                ("q3", "a"): {"q1",},

            }
        )

        cases = (
            ("", True),
            ("a", True),
            ("baba", True),
            ("baa", True),
            ("b", False),
            ("b", False),
            ("bb", False),
            ("babba", False),
        )

        for string, solution in cases:
            print(string)
            accepted = nfa.accepts(string)
            self.assertIs(accepted, solution, f"Error for {string}")
