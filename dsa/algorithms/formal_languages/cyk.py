from collections import defaultdict

import numpy as np
from numpy.typing import NDArray

from dsa.algorithms.formal_languages.types import (
    Nonterminal,
    sentencetype
)
from dsa.algorithms.formal_languages.context_free import Grammar
from dsa.algorithms.formal_languages.cnf_tools import chomsky_normal_form


class CYKParser:
    def __init__(self, G: Grammar) -> None:
        self.G = chomsky_normal_form(G)
        self.nonterms_inv = {nt: i for i, nt in enumerate(self.G.nonterminals)}
        self.terms_inv = {term: i for i, term in enumerate(self.G.terminals)}
        
        # Collect binary_productions (Na -> Nb Nc) and reverse unit productions (Na -> a)
        self.unit_prods_inv: dict[str, list[int]] = defaultdict(list)
        self.binary_prods: list[tuple[int, int, int]] = []

        for Na, prods in self.G.productions.items():
            Na_ind = self.nonterms_inv[Na]
            for p in prods:
                match len(p):
                    case 1:
                        if isinstance(p[0], str):
                            self.unit_prods_inv[p[0]].append(Na_ind)
                        #
                    case 2:
                        Nb, Nc = p
                        if isinstance(Nb, Nonterminal) and isinstance(Nc, Nonterminal):
                            Nb_ind, Nc_ind = map(self.nonterms_inv.__getitem__, (Nb, Nc))
                            self.binary_prods.append((Na_ind, Nb_ind, Nc_ind))
                        #
                    #
                #
            #
        #
    
    def is_producible(self, sentence: sentencetype) -> bool:
        # number of symbols in the sentence
        if sentence == ():
            return sentence in self.G.productions[self.G.start_symbol]
        n = len(sentence)
        r = len(self.G.nonterminals)

        shape = (n, n, r)
        P: NDArray[np.bool_] = np.full(shape, False, dtype=np.bool_)
        back: NDArray[np.object_] = np.empty(shape, dtype=object)
        for ind in np.ndindex(*shape):
            back[*ind] = []

        # First step: note which rules can produce each of the characters in the final string
        for s in range(n):
            symbol: str = sentence[s]
            for v in self.unit_prods_inv[symbol]:
                P[0, s, v] = True
            #
        
        # DP step: break into substrings of varying lengths and shifts, noting which rules produce each
        for i in range(1, n):  # iterate all substring lengths
            for s in range(n - i):  # substring start positions
                for p in range(i):  # positions to cut substring into left/right parts
                    cut = p + 1
                    for a, b, c in self.binary_prods:
                        left_producible = P[p][s][b]
                        right_producible = P[i-cut][s+cut][c]
                        if left_producible and right_producible:
                            P[i, s, a] = True
                            tup = (p, b, c)
                            back[i, s, a].append(tup)
                        #
                    #
                #
            #
        
        res = P[n-1][0][0]
        return res
