from copy import deepcopy
from dataclasses import dataclass
import random
from typing import Iterable, Iterator, NamedTuple, TypeAlias


class InvalidGrammarError(Exception):
    pass


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


@dataclass(init=False)
class Grammar:
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


def produce_random(
        grammar: Grammar,
        random_state: random.Random|int|None=None,
        from_symbol: Nonterminal|None=None,
        depth: int=0,
        target_max_depth=20
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
    
    # Choose a random production.
    options = grammar.productions[from_symbol]
    weights = [1.0 for _ in options]
    
    # If we're exceeding the target depth, choose only among terminal productions, if any
    if depth >= target_max_depth:
        all_terms = [all(isinstance(elem, Nonterminal) for elem in opt) for opt in options]
        if any(all_terms):
            weights = [int(at) for at in all_terms]
        #

    # Use one of the productions for the current nonterminal at random        
    choice = random_state.choices(options, weights=weights, k=1)[0]

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


def represent_grammar_as_string(grammar: Grammar) -> str:
    """Represents a grammar as a string, with production rules represented as e.g.
    S → ('a', A, 'a').
    Productions of the start symbol as displayed at the top."""
    
    nt_order = sorted(grammar.nonterminals, key = lambda nt: (nt != grammar.start_symbol, nt))
    lines: list[str] = []

    for nt in nt_order:
        for prod in grammar.productions[nt]:
            mapped = ('ε' if not prod else str(prod))
            lines.append(f"{nt} → {mapped}")

    res = "\n".join(lines)
    return res
