from typing import Sequence
import unittest

from dsa.automata.finite_state_machine import FiniteStateMachine


fsm1: FiniteStateMachine[str, int] = FiniteStateMachine(
    states={"q1", "q2"},
    alphabet={0, 1},
    transitions={
        ("q1", 0): "q1",
        ("q1", 1): "q2",
        ("q2", 0): "q1",
        ("q2", 1): "q2",
    },
    initial_state="q1",
    final_states=set(["q2"])
)


cases: list[tuple[FiniteStateMachine, Sequence, bool]] = [
    # Example 1.7 in Sipser
    (fsm1, [1, 1, 0, 1], True),
    (fsm1, [1, 1, 0], False)
]


class TestFSM(unittest.TestCase):
    def test_acceptance(self):
        for machine, string, valid in cases:
            accepted = machine.accepts(string)
            self.assertIs(accepted, valid)
        #
    #
