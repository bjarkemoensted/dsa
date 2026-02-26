"""Tooling for converting a grammar to Chomsky Normal Form (CNF) and testing CNF."""

from dsa.algorithms.formal_languages.context_free import (
    get_useless_symbols,
    Grammar,
    Nonterminal
)


def grammar_is_cnf(G: Grammar) -> bool:
    """Determines whether a grammar is CNF.
    Following Hopcroft & Ullman, CNF is defined as:
    1) No empty production ε
    2) No 'useless symbols' (nonterminals that are unreachable or have no productions)
    3) Only productions rules of the forms:
        A → BC
        A → a
    """
    
    # non-CNF if there are useless symbols
    useless_symbols = get_useless_symbols(G)
    if len(useless_symbols) != 0:
        return False
    
    # Check for empty productions, or rules that aren't splits (A → BC) or string productions (A → a)
    for prods in G.productions.values():
        for p in prods:
            empty = len(p) == 0
            if empty:
                return False
            
            split = len(p) == 2 and all(isinstance(nt, Nonterminal) for nt in p)
            string_ = len(p) == 1 and all(isinstance(s, str) for s in p)
            if not (split or string_):
                return False
            #
        #
    return True
