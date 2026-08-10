from dataclasses import dataclass

from typing import Sequence


@dataclass
class FiniteStateMachine[Q, S]:
    states: set[Q]
    alphabet: set[S]
    transitions: dict[tuple[Q, S], Q]
    initial_state: Q
    final_states: set[Q]

    def __post_init__(self) -> None:
        if not self.is_valid():
            raise RuntimeError

    def is_valid(self) -> bool:
        requirements = (
            self.initial_state in self.states,
            self.final_states.issubset(self.states)
        )

        return all(requirements)
    #

    def accepts(self, string: Sequence[S]) -> bool:
        state = self.initial_state
        for character in string:
            if character not in self.alphabet:
                return False
            state = self.transitions[(state, character)]

        return state in self.final_states
    #
