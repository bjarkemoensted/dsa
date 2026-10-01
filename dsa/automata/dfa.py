from collections.abc import Sequence
from dataclasses import dataclass, field

from dsa.automata.automaton_base import AutomatonBase


@dataclass
class DFA[Q, S](AutomatonBase):
    """Deterministic finite state automaton. Follows section 1.1 in Sipser"""

    transitions: dict[tuple[Q, S], Q] = field(default_factory=dict)

    def is_valid(self) -> bool:
        # Require the set of states to contain all states in the transition rules
        transition_states = set().union(*({u, v} for (u, _), v in self.transitions.items()))
        res = transition_states.issubset(self.states) and super().is_valid()
        return res

    def accepts(self, string: Sequence[S]) -> bool:
        state = self.initial_state
        for character in string:
            if character not in self.alphabet:
                return False
            try:
                state = self.transitions[(state, character)]
            except KeyError:
                return False

        return state in self.final_states