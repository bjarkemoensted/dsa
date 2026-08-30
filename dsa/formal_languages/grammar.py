from collections.abc import Iterator
from copy import deepcopy
from dataclasses import dataclass
from typing import Unpack

from dsa.formal_languages import parse_trees
from dsa.formal_languages.types import (
    InvalidGrammarError,
    Nonterminal,
    ProductionType,
    SentenceType,
    SententialType,
    SymbolType,
)


def _get_distinct_symbols[T](productions: ProductionType, target_class: type[T]) -> tuple[T, ...]:
    """Takes a dict with production rules. Returns a tuple of the distinct symbols of the specified class."""

    seen: set[T] = set()
    keep: list[T] = []

    candidates: list[SymbolType] = list(productions.keys())
    candidates += [symbol for prods in productions.values() for body in prods for symbol in body]

    for elem in candidates:
        if not isinstance(elem, target_class) or elem in seen:
            continue
        seen.add(elem)
        keep.append(elem)
    
    return tuple(keep)


@dataclass(init=False)
class CFG:
    """Represents a context-free grammar."""

    nonterminals: tuple[Nonterminal, ...]
    terminals: tuple[str, ...]
    productions: ProductionType
    start_symbol: Nonterminal

    def __init__(self, production_rules: ProductionType, start_symbol: Nonterminal) -> None:
        self.productions = deepcopy(production_rules)
        self.start_symbol = start_symbol

        self.terminals = _get_distinct_symbols(self.productions, str)
        self.nonterminals = _get_distinct_symbols(self.productions, Nonterminal)
        check_grammar_is_valid(self)

    def iter_rhs(self) -> Iterator[SententialType]:
        """Iterate over each individual production RHS"""
        for prods in self.productions.values():
            yield from prods
    
    def iter_produced_symbols(self) -> Iterator[SymbolType]:
        """Iterate over each produced symbol, i.e. each individual symbol
        in each production, so if the grammar is
            S → a | ab | B
            B → c | ε
        this will iterate over ('a',), ('a', 'b'), (B,), ('c',), ()"""
        for p in self.iter_rhs():
            yield from p

    @property
    def ascii(self) -> str:
        """Represents a grammar as a string, with production rules represented as e.g.
        S → ('a', A, 'a').
        Productions of the start symbol as displayed at the top."""
        
        # Order nonterminals alphabetically, except starting with the start symbol
        nt_order = sorted(self.productions.keys(), key = lambda nt: (nt != self.start_symbol, nt))
        lines: list[str] = []

        for nt in nt_order:
            these_prods = ['ε' if not symbol else str(symbol) for symbol in self.productions[nt]]
            prod_rep = " | ".join(these_prods)
                
            lines.append(f"{nt} → {prod_rep}")

        res = "\n".join(lines)
        return res

    
    def random_sentence(self, **kwargs: Unpack[parse_trees.GenKwargs]) -> SentenceType:
        """Produces a random sentence"""
        res = parse_trees.produce_random_sentence(
            from_symbol=self.start_symbol,
            productions=self.productions,
            **kwargs
        )

        return res
    
    def random_string(self, **kwargs: Unpack[parse_trees.GenKwargs]) -> str:
        return "".join(self.random_sentence(**kwargs))

    def brute_force_sentences(self, max_tokens: int) -> set[SentenceType]:
        brute = parse_trees.brute_force_sentences(
            from_symbol=self.start_symbol,
            productions=self.productions,
            max_tokens=max_tokens
        )

        res = set(brute)

        return res


def check_grammar_is_valid(G: CFG) -> None:
    """Checks that a grammar is valid, raising InvalidGrammarError if not."""

    # Check that terminals are strings
    if not all(isinstance(term, str) for term in G.terminals):
        raise InvalidGrammarError(f"Grammar must have string terminals. Got {G.terminals}")
    # Check nonterminals
    if not G.nonterminals or not all(isinstance(nonterm, Nonterminal) for nonterm in G.nonterminals):
        raise InvalidGrammarError(f"Grammar must have 1+ Nonterminals. Got {G.nonterminals}")

    # Check that both terminals and nonterminals are distinct
    if len(G.nonterminals) != len(set(G.nonterminals)):
        raise InvalidGrammarError("Nonterminals must be distinct")
    if len(G.terminals) != len(set(G.terminals)):
        raise InvalidGrammarError("Terminals must be distinct")
    
    # Check that the nonterminals attribute matches production rules
    nonterms_prod = set(G.productions.keys())
    terms_prod: set[str] = set()
    for prod in G.productions.values():
        for p in prod:
            nonterms_prod |= {symbol for symbol in p if isinstance(symbol, Nonterminal)}
            terms_prod |= {symbol for symbol in p if isinstance(symbol, str)}
    if nonterms_prod != set(G.nonterminals):
        raise InvalidGrammarError("Nonterminals do not match production rules")
    if terms_prod != set(G.terminals):
        raise InvalidGrammarError("Terminals do not match production rules")

    # Check that every nonterminal has a production
    _missing = sorted(set(G.nonterminals) - set(G.productions.keys()))
    if _missing:
        raise InvalidGrammarError(f"Some nonterminals have no productions: {', '.join(map(str, _missing))}")
