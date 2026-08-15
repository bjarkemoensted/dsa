from abc import abstractmethod, ABC
from dataclasses import dataclass

from typing import Sequence


EPSILON = None


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
    transitions: dict[tuple[Q, S|None], set[Q]]

    def _get_epsilon_transitions(self, *states: Q) -> set[Q]:
        """Given some states, returns the set of other states reachable via epsilon transitions"""
        res: set[Q] = set()
        front = set(states)
        seen = front
        while front:
            neighbors = set.union(*(self.transitions.get((state, EPSILON), set()) for state in front))
            new_ = neighbors - seen
            seen |= new_
            res |= new_
            front = new_

        return res
    
    def accepts(self, string: Sequence[S]) -> bool:
        states = {self.initial_state} | self._get_epsilon_transitions(self.initial_state)
        for character in string:
            # No match if there's no states left to iterate from
            if not states:
                break
            # Consume next character
            states = set.union(*(self.transitions.get((state, character), set()) for state in states))
            # Consider empty string transitions
            states |= self._get_epsilon_transitions(*states)

        end_states = states.intersection(self.final_states)
        res = len(end_states) > 0
        return res

    # TODO: regex parsing/Thompson's construction