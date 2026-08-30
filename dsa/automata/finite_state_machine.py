from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Self


class Epsilon:
    """Singleton for epsilon-transitions.
    This is just to avoid using None to represent the input for an epsilon
    transition, as None might be a valid character in an alphabet as well"""

    _inst: Self|None = None

    def __new__(cls) -> Self:
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst

    def __repr__(self) -> str:
        return "ε"


EPSILON = Epsilon()


@dataclass
class AutomatonBase[Q, S](ABC):
    """Base class for automata"""

    states: set[Q]
    alphabet: set[S]
    initial_state: Q
    final_states: set[Q]

    def __post_init__(self) -> None:
        if not self.is_valid():
            raise RuntimeError(f"Invalid automaton: {self}")

    def is_valid(self) -> bool:
        """Checks whether the automaton is valid"""
        requirements = (
            self.initial_state in self.states,
            self.final_states.issubset(self.states)
        )

        return all(requirements)

    @abstractmethod
    def accepts(self, string: Sequence[S]) -> bool:
        """Check whether the automaton recognizes some string"""
        raise NotImplementedError


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


@dataclass
class NFA[Q, S](AutomatonBase):
    transitions: dict[tuple[Q, S|Epsilon], set[Q]]

    def is_valid(self) -> bool:
        # Require the set of states to contain all states in the transition rules
        trans_sources = {u for u, _ in self.transitions}
        trans_targets = set().union(*self.transitions.values())
        res = (trans_sources | trans_targets).issubset(self.states) and super().is_valid()
        return res

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
        """Whether the automaton accepts the input string"""

        # Running set of states reachable after each character.
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

    def display_transitions(self) -> None:
        """Helper method for displaying the transitions in a somewhat easy to read format"""
        for (u, c), targets in sorted(self.transitions.items(), key=str):
            s = f"   {u} "
            if u == self.initial_state:
                s = f"-> {u} "
            elif u in self.final_states:
                s = f"  ({u})"            
            for v in targets:
                vs = f" {v} "
                if v in self.final_states:
                    vs = f"({v})"
                print(f"{s} -- {c} --> {vs}")
