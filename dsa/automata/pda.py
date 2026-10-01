from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Iterable, Iterator

from dsa.automata.automaton_base import EPSILON, AutomatonBase
from dsa.utils import Sentinel


@dataclass(frozen=True)
class Configuration[Q, S]:
    state: Q
    stack: tuple[S|Sentinel, ...]

    def __repr__(self) -> str:
        return f"<{self.state}, {self.stack}>"


def _push[T](stack: tuple[T|Sentinel, ...], elem: T|Sentinel) -> tuple[T|Sentinel, ...]:
    if elem is EPSILON:
        return stack
    else:
        return stack + (elem,)


@dataclass
class PDA[Q, S](AutomatonBase):
    """Pushdown automaton. Follows section 2.2 in Sipser"""

    stack_alphabet: set[S]  # TODO do we need to explicitly pass this? Or simpler to just assume same alphabet?
    transitions: dict[tuple[Q, S|Sentinel, S|Sentinel], tuple[Q, S|Sentinel]] = field(default_factory=dict)

    def is_valid(self) -> bool:
        # Require the set of states to contain all states in the transition rules
        trans_from = (q for q, _, _ in self.transitions)
        trans_to = (q for q, _ in self.transitions.values())
        transition_states = set().union(trans_from, trans_to)

        transition_states_valid = transition_states.issubset(self.states)
        stack_alphabet_valid = self.stack_alphabet.issubset(self.alphabet)

        parts = (
            transition_states_valid,
            stack_alphabet_valid,
            super().is_valid()
        )
        res = all(parts)
        return res

    def lookup_transitions(
            self,
            input_symbol: S|Sentinel,
            configurations: Iterable[Configuration[Q, S]],
            ) -> Iterator[Configuration[Q, S]]:
        """Given a current configuration and an input symbol, determines the subsequent configuration,
        if any (None is returned if no transition is allowed)"""

        for c in configurations:
            # Attempt to proceed popping nothing (epsilon) from the stack
            transition_nopop = self.transitions.get((c.state, input_symbol, EPSILON))
            if transition_nopop is not None:
                q, s = transition_nopop
                yield Configuration(q, _push(c.stack, s))

            # Attempt to consume from stack
            if not c.stack:
                continue
            stack_symbol = c.stack[-1]
            transition_pop = self.transitions.get((c.state, input_symbol, stack_symbol))
            if transition_pop is not None:
                q, s = transition_pop
                yield Configuration(q, _push(c.stack[:-1], s))
        
    def epsilon_closure(self, configurations: set[Configuration[Q, S]]) -> set[Configuration[Q, S]]:
        seen: set[Configuration[Q, S]] = configurations
        front = configurations

        while front:
            front = {c for c in self.lookup_transitions(EPSILON, front) if c not in seen}
            seen |= front

        return seen

    def accepts(self, string: Sequence[S]) -> bool:
        c0: Configuration[Q, S] = Configuration(
            state=self.initial_state,
            stack=()
        )
        running = {c0}

        running = self.epsilon_closure(running)

        for symbol in string:
            # All ways to consume the next symbol from input
            running = set(self.lookup_transitions(symbol, running))
            # Add epsilon transitions
            running = self.epsilon_closure(running)

        res = any(c.state in self.final_states for c in running)
        return res
