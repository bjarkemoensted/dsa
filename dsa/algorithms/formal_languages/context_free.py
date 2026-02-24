from copy import deepcopy
from dataclasses import dataclass
import random
from typing import Iterable, NamedTuple, TypeAlias


class Nonterminal(NamedTuple):
    name: str

    def __hash__(self):
        return tuple.__hash__(self)

    def __eq__(self, other):
        # This is to avoid accidentally matching with a string
        return isinstance(other, Nonterminal) and tuple.__eq__(self, other)
    
    def __repr__(self):
        return self.name


productiontype: TypeAlias = dict[Nonterminal, list[tuple[Nonterminal|str, ...]]]


def _get_distinct_instances[T](values: Iterable[object], target_class: type[T]) -> tuple[T, ...]:
    """Takes an iterable of objects, and returns a tuple of the distinct instances of the specified class."""

    seen: set[T] = set()
    keep: list[T] = []
    for val in values:
        if not isinstance(val, target_class) or val in seen:
            continue
        keep.append(val)
        seen.add(val)
    
    return tuple(keep)


@dataclass(init=False)
class Grammar:
    nonterminals: tuple[Nonterminal, ...]
    terminals: tuple[str, ...]
    productions: productiontype
    start_symbol: Nonterminal

    def __init__(self, production_rules: productiontype, start_symbol: Nonterminal) -> None:
        self.productions = deepcopy(production_rules)
        self.start_symbol = start_symbol
        _all_symbols = [elem for item in production_rules.items() for elem in item]
        self.terminals = _get_distinct_instances(_all_symbols, str)
        self.nonterminals = _get_distinct_instances(_all_symbols, Nonterminal)

    def __post_init__(self) -> None:
        if not self.start_symbol in self.nonterminals:
            raise ValueError(
                f"The start symbol {self.start_symbol} is not among the nonterminals: {self.nonterminals}"
            )
        #
    #


def produce_random(
        grammar: Grammar,
        random_state: random.Random|int|None=None,
        from_symbol: Nonterminal|None=None,
        depth: int=0,
        target_max_depth=5
    ) -> tuple[str, ...]:
    """Produce a random sentence using the specified grammar.
    grammar: The grammar to use
    random_state: Either a random.Random instance, or int/None to be used as seed.
    from_symbol: The nonterminal to use for producing. Defaults to the start symbol.
    depth: current recursion depth.
    target_max_depth: Approximate max recusion depth desired. When exceeded, productions leading to terminals
        will be selected over nonterminals.
    """
    
    # Set up a random state if one is not provided
    if not isinstance(random_state, random.Random):
        _seed = random_state
        random_state = random.Random()
        random_state.seed(_seed)

    from_symbol = grammar.start_symbol if from_symbol is None else from_symbol
    
    parts: list[str] = []
    
    # Choose a random production. If we're getting too long, look for terminal productions
    options = grammar.productions[from_symbol]
    if depth >= target_max_depth:
        stopping_productions = [output for output in options if not any(isinstance(s, Nonterminal) for s in output)]
        options = stopping_productions or options

    # Use one of the productions for the current nonterminal at random        
    choice = random_state.choice(options)

    # Keep string productions, recursively resolve nonterminal productions
    for elem in choice:
        if isinstance(elem, str):
            parts.append(elem)
        elif isinstance(elem, Nonterminal):
            recursed = produce_random(
                grammar=grammar,
                random_state=random_state,
                from_symbol=elem,
                depth=depth+1,
                target_max_depth=target_max_depth
            )
            parts.extend(recursed)
        else:
            raise TypeError
        #
    
    res = tuple(parts)

    return res
