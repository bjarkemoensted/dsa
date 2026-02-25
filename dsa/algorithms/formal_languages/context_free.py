from copy import deepcopy
from dataclasses import dataclass
from typing import Iterable, Iterator, NamedTuple, TypeAlias


class InvalidGrammarError(Exception):
    """Exception for when detecting rule violations when defining a grammar"""
    pass


class Nonterminal(NamedTuple):
    """A nonterminal.
    Storing this in a distinct class to avoid confusion with terminals (e.g. if relying on e.g. using
    upper case for nonterminals and lower case for terminals)"""

    name: str

    def __hash__(self):
        return tuple.__hash__(self)

    def __eq__(self, other):
        # This is to avoid accidentally matching with a string
        return isinstance(other, Nonterminal) and tuple.__eq__(self, other)
    
    def __repr__(self):
        return self.name


# Alias for production rules (mapping each nonterminal to a list of productions)
productiontype: TypeAlias = dict[Nonterminal, list[tuple[Nonterminal|str, ...]]]


def _iterate_symbols(production_rules: productiontype) -> Iterator[str|Nonterminal]:
    """Given some production rules, iterates over all symbols."""
    for nonterm, outputs in production_rules.items():
        yield nonterm
        for production in outputs:
            if not isinstance(production, tuple):
                raise TypeError  # just to make sure this isn't passed as a string (also iterable)
            for symbol in production:
                yield symbol
            #
        #
    #


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
    """Represents a context-free grammar."""

    nonterminals: tuple[Nonterminal, ...]
    terminals: tuple[str, ...]
    productions: productiontype
    start_symbol: Nonterminal

    def __init__(self, production_rules: productiontype, start_symbol: Nonterminal) -> None:
        self.productions = deepcopy(production_rules)
        self.start_symbol = start_symbol
        _all_symbols = list(_iterate_symbols(self.productions))
        self.terminals = _get_distinct_instances(_all_symbols, str)
        self.nonterminals = _get_distinct_instances(_all_symbols, Nonterminal)
        check_grammar_is_valid(self)
 
    @property
    def ascii(self) -> str:
        return represent_grammar_as_string(self)
    #


def check_grammar_is_valid(G: Grammar) -> None:
    """Checks that a grammar is valid, raising InvalidGrammarError if not."""

    # Check that terminals are strings
    if not all(isinstance(term, str) for term in G.terminals):
        raise InvalidGrammarError(f"Grammar must have string terminals. Got {G.terminals}")
    # Check nonterminals
    if not G.nonterminals or not all(isinstance(nonterm, Nonterminal) for nonterm in G.nonterminals):
        raise InvalidGrammarError(f"Grammar must have 1+ Nonterminals. Got {G.nonterminals}")
    
    # Check for 'dead ends' (all nonterminals must have productions)
    dead_ends = [nt for nt in G.nonterminals if nt not in G.productions]
    if dead_ends:
        raise InvalidGrammarError(f"Some nonterminals have no productions: {', '.join(map(str, dead_ends))}")
    #


def represent_grammar_as_string(grammar: Grammar) -> str:
    """Represents a grammar as a string, with production rules represented as e.g.
    S → ('a', A, 'a').
    Productions of the start symbol as displayed at the top."""
    
    # Order nonterminals alphabetically, except starting with the start symbol
    nt_order = sorted(grammar.nonterminals, key = lambda nt: (nt != grammar.start_symbol, nt))
    lines: list[str] = []

    for nt in nt_order:
        for prod in grammar.productions[nt]:
            mapped = ('ε' if not prod else str(prod))
            lines.append(f"{nt} → {mapped}")

    res = "\n".join(lines)
    return res
