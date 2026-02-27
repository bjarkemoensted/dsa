"""Tooling for converting a grammar to Chomsky Normal Form (CNF) and testing CNF.
This mainly uses the framework of Lange & Leiß (2009), also used on the Wikipedia page on Chomsky Normal Forms.
"""

from copy import deepcopy
from typing import Iterator, Literal, overload

from dsa.algorithms.formal_languages.context_free import (
    get_useless_symbols,
    Grammar,
    productiontype
)
from dsa.algorithms.formal_languages.types import Nonterminal


def grammar_is_cnf(G: Grammar, allow_empty_string_from_start=True) -> bool:
    """Determines whether a grammar is CNF.
    Following Hopcroft & Ullman, CNF is defined as:
    1) No 'useless symbols' (nonterminals that are unreachable or have no productions)
    2) Only productions rules of the forms:
        I)    A → BC
        II)   A → a
        III)  S → ε (if we allow empty strings from the start symbol)
    
    Allowing the special case where the start symbol may produce an empty string
    makes some things a bit more complicated, but allowes CNF grammars to produce empty strings.
    """
    
    # non-CNF if there are useless symbols
    useless_symbols = get_useless_symbols(G)
    if len(useless_symbols) != 0:
        return False
    
    # Check for empty productions, or rules that aren't splits (A → BC) or string productions (A → a)
    for nonterm, prods in G.productions.items():
        empty_ok = allow_empty_string_from_start and nonterm == G.start_symbol
        for p in prods:
            # Check empty
            empty = len(p) == 0

            # Check A → BC or A → a
            split = len(p) == 2 and all(isinstance(nt, Nonterminal) for nt in p)
            string_ = len(p) == 1 and all(isinstance(s, str) for s in p)

            # Check if the production has one of the three (I - III) forms allowed.
            cnf_rules_sat = split or string_ or (empty and empty_ok)
            if not cnf_rules_sat:
                return False
            #
        #
    
    return True



@overload
def _iter_rhs(
    productions: productiontype, flat: Literal[False] = False
) -> Iterator[tuple[str|Nonterminal, ...]]: ...

@overload
def _iter_rhs(
    productions: productiontype, flat: Literal[True]
) -> Iterator[str|Nonterminal]: ...

def _iter_rhs(
    productions: productiontype, flat: bool = False
) -> Iterator[str|Nonterminal|tuple[str|Nonterminal, ...]]:
    """Iterate over all productions.
    If flat is True, iterates over all symbols in all production right-hand-sides.
    Otherwise (default), iterates over individual productions, i.e. tuples of strings/Nonterminals."""

    for prods in productions.values():
        for p in prods:
            if flat:
                for elem in p:
                    yield elem
            else:
                yield p
            #
        #
    #


def _start(start_symbol: Nonterminal, productions: productiontype) -> Nonterminal:
    """START step - ensure no start symbols occur in any RHS productions.
    Modifies the production rules in-place and returns the new start symbol"""
    
    produced_nts = {symbol for symbol in _iter_rhs(productions, flat=True) if isinstance(symbol, Nonterminal)}
    # If the current start symbol doesn't occur in an RHS, there's nothing to do
    if start_symbol not in produced_nts:
        return start_symbol
    
    # Find a new, yet unused start symbol (retains the current if absent from all RHS)
    new_start = start_symbol
    suffix = -1
    while new_start in produced_nts:
        suffix += 1
        new_start = Nonterminal(f"{start_symbol}_{suffix}")

    # If introducing a new start symbol S_0, add a rule like S_0 -> S
    if new_start != start_symbol:
        productions[new_start] = [(start_symbol,)]    

    return new_start


def _term(productions: productiontype) -> None:
    """TERM step - ensure no rules have nonsolitary terminals"""
    
    # TODO implement
    raise NotImplementedError


def _bin(productions: productiontype) -> None:
    """BIN step - ensure no right-hand-sides have more than 2 non-terminals"""
    
    # TODO implement
    raise NotImplementedError


def _del(productions: productiontype) -> None:
    """DEL step - ensure no nonterminals apart from the start symbol produces the empty string"""
    
    # TODO implement
    raise NotImplementedError


def _unit(productions: productiontype) -> None:
    """UNIT step - ensure no nonterminals produce a single nonterminal"""
    
    # TODO implement
    raise NotImplementedError


def chomsky_normal_form(G: Grammar) -> Grammar:
    """Converts a grammar into an equivalent CNF grammar."""

    productions = deepcopy(G.productions)

    S0 = _start(start_symbol=G.start_symbol, productions=productions)
    assert all(symbol != S0 for symbol in _iter_rhs(productions, flat=True))

    _term(productions=productions)
    _bin(productions=productions)
    _del(productions=productions)
    _unit(productions=productions)

    res = Grammar(production_rules=productions, start_symbol=S0)
    return res
