from collections.abc import Sequence
from dataclasses import dataclass

from dsa.automata.automaton_base import EPSILON, AutomatonBase
from dsa.utils import Sentinel


@dataclass
class NFA[Q, S](AutomatonBase):
    transitions: dict[tuple[Q, S|Sentinel], set[Q]]

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
