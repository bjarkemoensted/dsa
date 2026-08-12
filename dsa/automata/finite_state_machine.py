from abc import abstractmethod, ABC
from dataclasses import dataclass

from typing import Sequence


@dataclass
class AutomatonBase[Q, S](ABC):
    states: set[Q]
    alphabet: set[S]
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

    @abstractmethod
    def accepts(self, string: Sequence[S]) -> bool:
        raise NotImplementedError
    #


@dataclass
class DFA[Q, S](AutomatonBase):
    transitions: dict[tuple[Q, S], Q]

    def accepts(self, string: Sequence[S]) -> bool:
        state = self.initial_state
        for character in string:
            if character not in self.alphabet:
                return False
            state = self.transitions[(state, character)]

        return state in self.final_states
    #


@dataclass
class NFA[Q, S](AutomatonBase):
    transitions: dict[tuple[Q, S], set[Q]]

    def accepts(self, string: Sequence) -> bool:
        states = {self.initial_state}
        for character in string:
            states = set.union(*(self.transitions[(state, character)] for state in states))

        end_states = states.intersection(self.final_states)
        res = len(end_states) > 0
        return res

    # TODOÆ epsilon transitions and regex parsing/Thompson's construction