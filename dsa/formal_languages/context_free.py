from copy import deepcopy
from dataclasses import dataclass
from typing import Iterable, Iterator, Unpack


from dsa.formal_languages.types import (
    InvalidGrammarError,
    Nonterminal,
    productiontype,
    sentencetype,
    sententialtype,
    symboltype,
)

from dsa.formal_languages import parse_trees


def _iterate_symbols(production_rules: productiontype, include_keys=True) -> Iterator[str|Nonterminal]:
    """Given some production rules, iterates over all symbols.
    If include_keys is True (default), also yields the keys in the dictionary, i.e. the LHS nonterminals
    in the production rules."""

    for nonterm, outputs in production_rules.items():
        if include_keys:
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
class CFG:
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

    def iter_rhs(self) -> Iterator[sententialtype]:
        """Iterate over each individual production RHS"""
        for prods in self.productions.values():
            for p in prods:
                yield p
            #
        #
    
    def iter_produced_symbols(self) -> Iterator[symboltype]:
        """Iterate over each produced symbol, i.e. each individual symbol
        in each production, so if the grammar is
            S → a | ab | B
            B → c | ε
        this will iterate over ('a',), ('a', 'b'), (B,), ('c',), ()"""
        for p in self.iter_rhs():
            for symbol in p:
                yield symbol
            #
        #

    @property
    def ascii(self) -> str:
        return represent_grammar_as_string(self)
    
    def random_sentence(self, **kwargs: Unpack[parse_trees.GenKwargs]) -> sentencetype:
        """Produces a random sentence"""
        res = parse_trees.produce_random_sentence(
            from_symbol=self.start_symbol,
            productions=self.productions,
            **kwargs
        )

        return res
    
    def random_string(self, **kwargs: Unpack[parse_trees.GenKwargs]) -> str:
        return "".join(self.random_sentence(**kwargs))

    def brute_force_sentences(self, max_tokens: int) -> set[sentencetype]:
        brute = parse_trees.brute_force_sentences(
            from_symbol=self.start_symbol,
            productions=self.productions,
            max_tokens=max_tokens
        )

        res = set(brute)

        return res


def get_useless_symbols(G: CFG) -> list[Nonterminal]:
    """Detects 'useless' symbols in the grammar, meaning nonterminals which
    do not appear in any derivation from the start symbol.
    Identifies which nonterminals are 1) reachable and 2) can produce any
    string (including the empty string)."""

    reachable: set[Nonterminal] = set()
    front: set[Nonterminal] = {G.start_symbol}

    # Determine nonterms reachable from the start symbol
    while front:
        reachable |= front
        heads = list(front)
        front = set()
        for head in heads:
            for prod in G.productions.get(head, []):
                for symbol in prod:
                    if isinstance(symbol, Nonterminal):
                        front.add(symbol)
                    #
                #
            #
        front -= reachable

    # Determine which of the nonterms can produce strings
    producing: set[Nonterminal] = set()
    # Keep updating until we don't detect more string-producers
    updated = True
    while updated:
        n_determined = len(producing)
        updated = False
        for head, productions in G.productions.items():
            for rhs in productions:
                # Nonterm can produce string if it can produce a string, or a string-producing nonterm
                stringmaker = any(isinstance(symbol, str) or symbol in producing for symbol in rhs) or not rhs
                if stringmaker:
                    producing.add(head)
                    producing |= {symbol for symbol in rhs if isinstance(symbol, Nonterminal)}
                #
            #
        updated = len(producing) != n_determined

    useful = reachable & producing
    useless = set(G.nonterminals) - useful

    return sorted(useless)


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
        #
    if nonterms_prod != set(G.nonterminals):
        raise InvalidGrammarError("Nonterminals do not match production rules")
    if terms_prod != set(G.terminals):
        raise InvalidGrammarError("Terminals do not match production rules")

    # Check that every nonterminal has a production
    _missing = sorted(set(G.nonterminals) - set(G.productions.keys()))
    if _missing:
        raise InvalidGrammarError(f"Some nonterminals have no productions: {', '.join(map(str, _missing))}")


def represent_grammar_as_string(grammar: CFG) -> str:
    """Represents a grammar as a string, with production rules represented as e.g.
    S → ('a', A, 'a').
    Productions of the start symbol as displayed at the top."""
    
    # Order nonterminals alphabetically, except starting with the start symbol
    nt_order = sorted(grammar.productions.keys(), key = lambda nt: (nt != grammar.start_symbol, nt))
    lines: list[str] = []

    for nt in nt_order:
        these_prods = ['ε' if not symbol else str(symbol) for symbol in grammar.productions[nt]]
        prod_rep = " | ".join(these_prods)
            
        lines.append(f"{nt} → {prod_rep}")

    res = "\n".join(lines)
    return res
