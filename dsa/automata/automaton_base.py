from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from dsa.utils import Sentinel

# Sentinel representing the empty string
EPSILON = Sentinel("ε")


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