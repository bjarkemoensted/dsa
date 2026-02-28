"""Tooling for converting a grammar to Chomsky Normal Form (CNF) and testing CNF.
This mainly uses the framework of Lange & Leiß (2009), also used on the Wikipedia page on Chomsky Normal Forms.
"""

from copy import deepcopy
from typing import Iterable, Iterator, Literal, overload

from dsa.algorithms.formal_languages.context_free import (
    get_useless_symbols,
    Grammar
)
from dsa.algorithms.formal_languages.types import (
    Nonterminal,
    productiontype
)


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
# TODO DELETE IF UNUSED!!!
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

    
class SymbolGenerator:
    """Handles generating symbols.
    This is basically just to keep the logic for, given variables like X, X_1, ...,
    to be able to generate distinct names, with incrementing suffixes."""

    def __init__(self, nonterms: Iterable[Nonterminal], separator="_") -> None:
        """nonterms: iterable of non-terminals which we'll be renaming
        separator: string for separating a nonterminal's base name from its numeric suffix.
            e.g. 'X_1' (base name 'X', suffix 1)"""

        self.separator = separator
        # Determine the maximum suffix for each base name
        self.counts: dict[str, int] = dict()
        for nt in nonterms:
            base, n = self.split(nt.name)
            n = 0 if n is None else n
            if n > self.counts.get(base, float("-inf")):
                self.counts[base] = n
            #
        #

    def split(self, s: str) -> tuple[str, int]:
        """Attempts to split a name into a base name and integer suffix, e.g.
        X_1 -> (X, 1).
        Returns None if no suffix, or if suffix can't be cast as integer (e.g. 'X_a')"""
        
        parts = s.split(self.separator)
        if len(parts) == 1:
            return s, 0
        
        suffix = parts[-1]
        prefix = self.separator.join(parts[:-1])
        try:
            return prefix, int(suffix)
        except ValueError:
            return s, 0
        #
    #

    def __call__(self, symbol: str|Nonterminal) -> Nonterminal:
        """Make a new nonterminal with a yet-unused name,
        by taking the base name for the nonterminal, incrementing
        its counter, and constructing a new Nonterminal with the resulting name
        Can also be passed a string"""
        
        s = symbol if isinstance(symbol, str) else symbol.name
        base, _ = self.split(s)
        try:
            self.counts[base] += 1
            n = self.counts[base]
            new_name = f"{base}{self.separator}{n}"
        except KeyError:
            self.counts[base] = 0
            new_name = base
        
        res = Nonterminal(new_name)

        return res
    #


class CNFConverter:
    def __init__(self, start_symbol: Nonterminal, productions: productiontype) -> None:
        self.start_symbol = start_symbol
        self.production_rules = deepcopy(productions)

        # Set up a renamer for when we need to introduce new nonterminals
        nonterms = {*self.production_rules.keys(), *self._produced_nts()}
        self.make_new_symbol = SymbolGenerator(nonterms=nonterms)

    def _produced_nts(self) -> Iterator[Nonterminal]:
        """Iterate over all each nonterminal in the production RHS"""
        for prods in self.production_rules.values():
            for p in prods:
                for elem in p:
                    if isinstance(elem, Nonterminal):
                        yield elem
                    #
                #
            #
        #

    def _start(self) -> None:
        """START step - ensure no start symbols occur in any RHS productions.
        Modifies the production rules in-place and returns the new start symbol"""
        
        # If the current start symbol doesn't occur in an RHS, there's nothing to do
        if self.start_symbol not in self._produced_nts():
            return
        
        # Find a new, yet unused start symbol (retains the current if absent from all RHS)
        new_start = self.make_new_symbol(self.start_symbol)
        assert new_start not in self.production_rules
        
        # If introducing a new start symbol S_1, add a rule like S_1 -> S
        self.production_rules[new_start] = [(self.start_symbol,)]
        self.start_symbol = new_start

    def _term(self) -> None:
        """TERM step - ensure no rules have nonsolitary terminals"""
        # Make a mapping from strings to nonterminals that produce only that string
        solitary_prods = dict()
        for nt, prods in self.production_rules.items():
            if len(prods) != 1:
                continue  # only look for productions of single strings
            for p in prods:
                if len(p) == 1 and all(isinstance(w, str) for w in p):
                    solitary_prods[p[0]] = nt  # register the nonterminal which produces this string
                #
            #
        
        # Now look for nonsolitary strings
        for nt, prods in list(self.production_rules.items()):
            for i, p in enumerate(prods):
                if len(p) <= 1:
                    continue  # productions must have at least two symbols to make a nonsolitary string
                
                # Find the indices and values of the string productions
                string_syms = [(ind, symbol) for ind, symbol in enumerate(p) if isinstance(symbol, str)]
                if not string_syms:
                    continue
                
                # Insert (new) nonterminals in place of the nonsolitary strings
                p_update = list(p)
                for ind, s in string_syms:
                    # If we don't already have a nonterminal producing this string, generate a new one
                    if s not in solitary_prods:
                        basename = f"N_{s}"  # choose a name like N_a for the terminal 'a'
                        new_nt = self.make_new_symbol(basename)
                        self.production_rules[new_nt] = [(s,)]
                        # Also note the nonterminal here, so we can reuse it
                        solitary_prods[s] = new_nt
                    
                    # Replace the string with the new nonterm, and add a new production rule like N_a -> 'a'
                    p_update[ind] = solitary_prods[s]
                self.production_rules[nt][i] = tuple(p_update)
            #
        #   

    def _bin(self) -> None:
        """BIN step - ensure no right-hand-sides have more than 2 non-terminals"""
    
        raise NotImplementedError
    
    def _del(self) -> None:
        """DEL step - ensure no nonterminals apart from the start symbol produces the empty string"""
    
        raise NotImplementedError
    
    def _unit(self) -> None:
        """UNIT step - ensure no nonterminals produce a single nonterminal"""
        raise NotImplementedError

    def convert(self) -> None:
        self._start()
        self._term()
        # TODO implement remaining!!!
        # self._bin()
        # self._del()
        # self._unit()
        


def chomsky_normal_form(G: Grammar) -> Grammar:
    """Converts a grammar into an equivalent CNF grammar."""

    converter = CNFConverter(start_symbol=G.start_symbol, productions=G.productions)
    converter.convert()
    res = Grammar(start_symbol=converter.start_symbol, production_rules=converter.production_rules)

    return res
