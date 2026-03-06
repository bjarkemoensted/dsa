from collections import defaultdict

import numpy as np
from numpy.typing import NDArray

from dsa.formal_languages.types import (
    Nonterminal,
    sentencetype
)
from dsa.formal_languages.context_free import CFG
from dsa.formal_languages.cnf_tools import chomsky_normal_form
from dsa.formal_languages.parse_trees import ParseForest, ParseForestNode, ParseNode


class CYKParser:
    """CYK Parser for determining if and how a sentence can be produced by a context-free grammar.
    This largely follows the pseudocode implementation on the Wikipedia article on the CYK algorithm:
        https://en.wikipedia.org/wiki/CYK_algorithm
    The main exception is the example there uses 1-indexing and does not seem to account for empty strings.
    The implementation here uses 0-indexing, and treats empty string similarly to any other sentence."""

    def __init__(self, G: CFG, assume_cnf=False) -> None:
        """Create a CYK Parser, using the input grammar.
        assume_cnf: If True, assumed the grammar is already on Chomsky Normal Form, and proceeds without
            converting it. If False, the grammar is converted into CNF."""

        self.G = G if assume_cnf else chomsky_normal_form(G)
        # Mapping from nonterminals to their index
        self.nonterms_inv = {nt: i for i, nt in enumerate(self.G.nonterminals)}
        
        # Collect empty productions, binary_productions (Na -> Nb Nc) and reverse unit productions (Na -> a)
        self.empty_prods: list[int] = []
        self.unit_prods_inv: dict[str, list[int]] = defaultdict(list)
        self.binary_prods: list[tuple[int, int, int]] = []

        for Na, prods in self.G.productions.items():
            Na_ind = self.nonterms_inv[Na]
            for p in prods:
                match len(p):
                    case 0:
                        # Register null-producing nonterminals
                        self.empty_prods.append(Na_ind)
                    case 1:
                        # Register terminal-producing nonterminals
                        if isinstance(p[0], str):
                            self.unit_prods_inv[p[0]].append(Na_ind)
                        #
                    case 2:
                        # Register binary productions
                        Nb, Nc = p
                        if isinstance(Nb, Nonterminal) and isinstance(Nc, Nonterminal):
                            Nb_ind, Nc_ind = map(self.nonterms_inv.__getitem__, (Nb, Nc))
                            self.binary_prods.append((Na_ind, Nb_ind, Nc_ind))
                        #
                    case _:
                        raise RuntimeError(f"Production contains too many symbols: {p}")
                    #
                #
            #
        #
    
    @property
    def start_symbol_index(self) -> int:
        ind = self.nonterms_inv[self.G.start_symbol]
        return ind

    def _parse(self, sentence: sentencetype) -> tuple[NDArray[np.bool_], NDArray[np.object_]]:
        """Parse the input sentence.
        Returns a tuple P, back
        P: a 3D array of bools, with P[i, j, k] indicating whether a substring of length i, starting at j
            is producible starting from nonterminal k.
        back: A similar array in which back[i, s, a] is a list of 3-tuples (p, b, c), indicating that
            the substring from s through s+i can be split at position p and the left and right parts produced
            by rule a -> b c
        """

        # number of symbols in the sentence
        n_chars = len(sentence)
        n = n_chars + 1  # need one more row so P[i, j, k] means substring with i chars (i=0 for empty)
        r = len(self.G.nonterminals)

        shape = (n, max(n-1, 1), r)
        P: NDArray[np.bool_] = np.full(shape, False, dtype=np.bool_)
        back: NDArray[np.object_] = np.empty(shape, dtype=object)
        for ind in np.ndindex(*shape):
            back[*ind] = []
        
        # Note which nonterminals can produce empty strings
        P[0, 0, self.empty_prods] = True

        # First step: note which rules can produce each of the characters in the final string
        for s in range(n-1):
            symbol: str = sentence[s]
            for v in self.unit_prods_inv[symbol]:
                P[1, s, v] = True
            #
        
        # DP step: break into substrings of varying lengths and shifts, noting which rules produce each
        for i in range(2, n):  # iterate all substring lengths (start at 2 bc we already did shorter strings)
            for s in range(n - i):  # substring start positions
                for p in range(1, i):  # positions to cut substring into left/right parts
                    for a, b, c in self.binary_prods:
                        # Look for binary productions which produce the left and right sides
                        left_producible = P[p][s][b]
                        right_producible = P[i-p][s+p][c]
                        if left_producible and right_producible:
                            # Register that nonterminal a can produce substring s through s+i
                            P[i, s, a] = True
                            # Register that a -> b c produces the left(b) and right(c) parts, splitting substring at p
                            tup = (p, b, c)
                            back[i, s, a].append(tup)
                        #
                    #
                #
            #
        
        return P, back

    def _parse_table_accept(self, P: NDArray[np.bool_]) -> bool:
        """Use the CYK parse table for a string, to determine whether the string
        is a member of the language represented by the grammar"""
        producible = P[-1][0][self.start_symbol_index]
        res = producible.item()  # convert numpy bool to native type
        return res

    def accepts(self, sentence: sentencetype) -> bool:
        """Determines whether the sentence is producible by the grammar"""
        # Build the parse table
        P, _ = self._parse(sentence=sentence)
        return self._parse_table_accept(P)
    #

    def parse(self, sentence: sentencetype) -> ParseNode|None:
        """Parse the sentence and return a parse tree (its root node) if the sentence is accepted.
        If not accepted, None is returned instead."""
        
        forest = self.make_parse_forest(sentence=sentence)
        try:
            return next(iter(forest))
        except StopIteration:
            return None

    def make_parse_forest(self, sentence: sentencetype) -> ParseForest:
        """Encode every parse tree for the sentence in a parse forest."""

        P, back = self._parse(sentence=sentence)

        accept = self._parse_table_accept(P)
        root = None
        if accept:
            root = build_parse_forest(
                G=self.G,
                sentence=sentence,
                back=back,
                A=self.start_symbol_index
            )
        
        res = ParseForest(root=root)

        return res


def build_parse_forest(
        G: CFG,
        sentence: sentencetype,
        back: NDArray[np.object_],
        A: int,
        length: int=-1,
        start: int=0,
    ) -> ParseForestNode:
    """Build a compact parse forest to represent all parse trees for a sentence/grammar combination.
    nonterminals: tuple of the nonterminals in the (CNF) grammar
    sentence: The sentence parsed
    back: Backpointing triples encoding how each head in the production rules can produce which substrings
    length: Length of the current substring (initially the sentence length)
    start: The starting index of the current substring (initially 0)
    A: The current production head (initially the start symbol)"""
    
    if length == -1:
        length = len(sentence)
        assert G.nonterminals[A] == G.start_symbol

    # Make a PFN for the productions from A
    node = ParseForestNode(
        A=A,
        start=start,
        length=length,
        nonterminals=G.nonterminals,
        sentence=sentence
    )

    # Return if we're down to a single symbol
    if length == 1:
        last_char = sentence[start:start+length]
        assert last_char in G.productions[G.nonterminals[A]]
        return node

    # Otherwise, recurse on partitionings into left and right substrings
    for split, B, C in back[length, start, A]:
        left = build_parse_forest(
            G=G,
            back=back,
            start=start,
            length=split,
            A=B,
            sentence=sentence
        )
        right = build_parse_forest(
            G=G,
            back=back,
            start=start + split,
            length=length - split,
            A=C,
            sentence=sentence
        )

        node.alternatives.append((left, right))
    
    return node
