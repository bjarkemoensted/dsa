from typing import Sequence
import unittest

from dsa.automata.finite_state_machine import AutomatonBase, DFA, NFA


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
nfa1: NFA[str, int] = NFA(
    **(dfa_kwargs_1 | {"transitions": {k: {v,} for k, v in transitions.items()}})  # type: ignore
)

cases: list[tuple[AutomatonBase, Sequence, bool]] = [
    # Example 1.7 in Sipser
    (dfa1, [1, 1, 0, 1], True),
    (dfa1, [1, 1, 0], False),
    (nfa1, [1, 1, 0, 1], True),
    (nfa1, [1, 1, 0], False),
]


class TestFSM(unittest.TestCase):
    def test_acceptance(self) -> None:
        for machine, string, valid in cases:
            accepted = machine.accepts(string)
            self.assertIs(accepted, valid)
        #
    
    def test_invalid_machine_raises_error(self) -> None:
        invalid_kwargs = [
            {"final_states": {"x",}},
            {"initial_state": 99}
        ]

        for d in invalid_kwargs:
            with self.assertRaises(RuntimeError):
                DFA(**(dfa_kwargs_1 | d))  # type: ignore
            #
        #
    
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
        #
    #
