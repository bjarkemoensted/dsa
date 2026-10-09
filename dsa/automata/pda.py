from collections.abc import Sequence
from dataclasses import dataclass, field
from itertools import count
from typing import Iterable, Iterator

from dsa.automata.automaton_base import EMPTY_STACK, EPSILON, AutomatonBase
from dsa.formal_languages.grammar import CFG
from dsa.formal_languages.types import Nonterminal
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
class PDA[Q, S, SA](AutomatonBase):
    """Pushdown automaton. Follows section 2.2 in Sipser"""

    stack_alphabet: set[SA]  # TODO do we need to explicitly pass this? Or simpler to just assume same alphabet?
    transitions: dict[tuple[Q, S|Sentinel, SA|Sentinel], set[tuple[Q, SA|Sentinel]]] = field(default_factory=dict)

    def is_valid(self) -> bool:
        # Require the set of states to contain all states in the transition rules
        trans_from = (q for q, _, _ in self.transitions)
        trans_to = (q for tups in self.transitions.values() for q, _ in tups)
        transition_states = set().union(trans_from, trans_to)

        transition_states_valid = transition_states.issubset(self.states)

        parts = (
            transition_states_valid,
            super().is_valid()
        )
        res = all(parts)
        return res

    def lookup_transitions(
            self,
            input_symbol: S|Sentinel,
            configurations: Iterable[Configuration[Q, SA]],
            ) -> Iterator[Configuration[Q, SA]]:
        """Given a current configuration and an input symbol, determines the subsequent configuration,
        if any (None is returned if no transition is allowed)"""

        for c in configurations:
            # Attempt to proceed popping nothing (epsilon) from the stack
            transitions_nopop = self.transitions.get((c.state, input_symbol, EPSILON))
            if transitions_nopop is not None:
                yield from (Configuration(q, _push(c.stack, s)) for q, s in transitions_nopop)

            # Attempt to consume from stack
            if not c.stack:
                continue
            stack_symbol = c.stack[-1]
            transitions_pop = self.transitions.get((c.state, input_symbol, stack_symbol))
            if transitions_pop is not None:
                yield from (Configuration(q, _push(c.stack[:-1], s)) for q, s in transitions_pop)
        
    def epsilon_closure(self, configurations: set[Configuration[Q, SA]]) -> set[Configuration[Q, SA]]:
        seen: set[Configuration[Q, SA]] = configurations
        front = configurations

        while front:
            front = {c for c in self.lookup_transitions(EPSILON, front) if c not in seen}
            seen |= front

        return seen

    def accepts(self, string: Sequence[S]) -> bool:
        c0: Configuration[Q, SA] = Configuration(
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



# TODO Cleanup and add tests!!!
def make_pda(cfg: CFG) -> PDA[int, str, str|Nonterminal]:
    node_gen = count(start=0, step=1)

    q_i = next(node_gen)
    q_pre = next(node_gen)
    q_loop = next(node_gen)
    q_f = -1

    S = cfg.start_symbol

    # TODO consider making states, alphabet, stack alphabet optional, and inferring from transitions if not provided!!!
    transitions: dict[tuple[int, str|Sentinel, str|Sentinel|Nonterminal], set[tuple[int, str|Sentinel|Nonterminal]]] = {
        (q_i, EPSILON, EPSILON): {(q_pre, EMPTY_STACK)},
        (q_pre, EPSILON, EPSILON): {(q_loop, S)},
        (q_loop, EPSILON, EMPTY_STACK): {(q_f, EPSILON)}
        #("q2", 0, EPSILON): ("q2", 0),
    }

    def add_transition(
            u: int,
            input_symbol: str|Sentinel,
            stack_symbol: str|Sentinel|Nonterminal,
            v: int,
            new_stack_sym: str|Sentinel|Nonterminal
            ) -> None:
        
        nonlocal transitions
        key_ = (u, input_symbol, stack_symbol)
        if key_ not in transitions:
            transitions[key_] = set()
        transitions[key_].add((v, new_stack_sym))

    def add_chain(nt: Nonterminal, production: tuple[str|Nonterminal, ...]) -> None:
        nonlocal node_gen
        u = q_loop
        if len(production) == 0:
            add_transition(u, EPSILON, nt, u, EPSILON)
            return

        # TODO has to be a more elegant way of doing this!!!
        v = u
        for i, symbol in enumerate(reversed(production)):
            last = i == len(production) - 1
            first = i == 0
            v = q_loop if last else next(node_gen)
            consume = nt if first else EPSILON
            add_transition(u, EPSILON, consume, v, symbol)
            u = v


    for symbol in cfg.terminals:
        # Add a transition which just pops the symbol from the stack
        add_transition(q_loop, symbol, symbol, q_loop, EPSILON)

    for nt, productions in cfg.productions.items():
        for prod in productions:
            add_chain(nt, prod)

    k, v = zip(*transitions.items())
    stack_alphabet = {elem for _, elem, _ in k} | {elem for out in v for _, elem in out}
    states = {elem for elem, _, _ in k} | {elem for v_ in v for elem, _ in v_}
    alphabet = {elem for _, elem, _ in k}


    res: PDA[int, str, str|Nonterminal] = PDA(
        states=states,
        alphabet=alphabet,
        initial_state=q_i,
        final_states={q_f},  # !!!
        stack_alphabet=stack_alphabet,
        transitions=transitions,
    )

    return res
