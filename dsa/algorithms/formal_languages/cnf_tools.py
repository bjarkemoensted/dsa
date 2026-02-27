"""Tooling for converting a grammar to Chomsky Normal Form (CNF) and testing CNF."""

from dsa.algorithms.formal_languages.context_free import (
    get_useless_symbols,
    Grammar,
    Nonterminal
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
