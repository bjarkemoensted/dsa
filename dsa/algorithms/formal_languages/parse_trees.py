from __future__ import annotations
import random
from typing import Iterable, Iterator, TypedDict, Unpack

import anytree  # type: ignore

from dsa.algorithms.formal_languages.types import (
    DerivationError,
    is_sentence,
    Nonterminal,
    productiontype,
    sentencetype,
    sententialtype
)


class GenKwargs(TypedDict, total=False):
    """Reusable kwargs type for sentence generation"""
    random_state: random.Random | int | None
    target_max_depth: int | None


class ParseNode(anytree.AnyNode):
    """Represents a node in a parse tree."""

    def __init__(
            self,
            symbol: str|Nonterminal,
            parent: ParseNode|None=None,
            children: Iterable[ParseNode]|None=None
        ) -> None:
        """Create a node.
        symbol: The symbol which the node represents. String for terminals, otherwise Nonterminal.
        parent: The parent node. None for root node.
        children: Optional: iterable of child nodes."""

        self.symbol = symbol
        self.parent = parent
        if children:
            self.children = children
        #

    def ascii_tree(self) -> str:
        """Represents the tree as text"""
        s = str(anytree.RenderTree(self))
        return s

    def sentence(self) -> str:
        """Returns the sentence from this node as a string"""
        s = "".join(self.iter_sentence())
        return s

    def iter_sentence(self) -> Iterator[str]:
        """Iterates over the sentence produced from this node."""

        if isinstance(self.symbol, Nonterminal):
            # For nonterminals, continue iterating over child nodes
            for child in self.children:
                yield from child.iter_sentence()
            #
        elif isinstance(self.symbol, str):
            # For terminals just use the node's symbol
            assert self.is_leaf
            yield self.symbol
        else:
            raise TypeError
        #

    def __repr__(self):
        return repr(self.symbol)


def grow_random_parse_tree(
        from_symbol: Nonterminal|str,
        productions: productiontype,
        parent: ParseNode|None=None,
        depth: int=0,
        random_state: random.Random|int|None=None,
        target_max_depth: int|None=None
    ) -> ParseNode:
    """Produce a parse tree for a random sentence using the specified grammar.
    grammar: The grammar to use
    random_state: Either a random.Random instance, or int/None to be used as seed.
    from_symbol: The nonterminal to use for producing. Defaults to the start symbol.
    depth: current recursion depth.
    target_max_depth: Approximate max recusion depth desired. When exceeded, productions leading to terminals
        will be selected over nonterminals.
    """
    
    target_max_depth = 20 if target_max_depth is None else target_max_depth
    # Create a node in the parse tree
    node = ParseNode(symbol=from_symbol, parent=parent)
    # If terminal, just return the node
    if not isinstance(from_symbol, Nonterminal):
        return node

    # Set up a random state if one is not provided
    if not isinstance(random_state, random.Random):
        _seed = random_state
        random_state = random.Random()
        random_state.seed(_seed)

    # Choose a random production.
    try:
        options = productions[from_symbol]
    except KeyError:
        raise DerivationError(f"No production rule for symbol: {from_symbol}")
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
        grow_random_parse_tree(
            from_symbol=elem,
            productions=productions,
            random_state=random_state,
            parent=node,
            depth=depth+1,
            target_max_depth=target_max_depth
        )

    return node


def produce_random_sentence(
        from_symbol: Nonterminal,
        productions: productiontype,
        depth: int=0,
        **kwargs: Unpack[GenKwargs]
    ) -> tuple[str, ...]:
    """Produce a random sentence using the specified grammar.
    See grow_random_parse_tree docstring for details."""

    root = grow_random_parse_tree(
        from_symbol=from_symbol,
        productions=productions,
        depth=depth,
        **kwargs
    )

    res = tuple(root.iter_sentence())
    return res


def determine_length_bounds(productions: productiontype) -> dict[Nonterminal, int]:
    """Takes production rules and returns a dict mapping each nonterminal to a lower bound
    on the number of terminals in sentences it may produce"""
    min_lengths = {nt: float("inf") for nt in productions.keys()}
    changed = True
    while changed:
        changed = False
        for nt, prods in productions.items():
            bounds = [[1 if isinstance(symbol, str) else min_lengths[symbol] for symbol in p] for p in prods]
            new_min = min(map(sum, bounds))
            if new_min != min_lengths[nt]:
                min_lengths[nt] = new_min
                changed = True
            #
        #
    #   

    res = {nt: int(bound) for nt, bound in min_lengths.items()}
    return res


def brute_force_sentences(
        from_symbol: Nonterminal,
        productions: productiontype,
        max_tokens: int
    ) -> set[tuple[str, ...]]:
    """Computes all sentences with length no greater than the specified
    number of tokens."""
    
    lower_bounds = determine_length_bounds(productions)
    res: set[sentencetype] = set()
    queue: list[sententialtype] = [(from_symbol,)]
    processed: set[sententialtype] = set(queue)
    
    while queue:
        
        current = queue.pop()
        # Stop if the allowed number of tokens exceeds/will exceed target
        sentence_lower_bound = sum(1 if isinstance(elem, str) else lower_bounds[elem] for elem in current)
        if sentence_lower_bound > max_tokens:
            continue
        
        # Add sentences to results
        if is_sentence(current):
            res.add(current)
            continue
        
        # Select a random nonterminal
        ind_nts = list((i, s) for i, s in enumerate(current) if isinstance(s, Nonterminal))
        replace_ind, symbol = random.choice(ind_nts)

        # Replace the nonterminal with all possible productions
        for rhs in productions[symbol]:
            new_sentential = (
                *current[:replace_ind],  # symbols left of the non-terminal
                *rhs,  # symbols produced by this non-terminal
                *current[replace_ind+1:]  # symbols right of the non-terminal
            )
            # If this sentential form is new, add to queue
            if new_sentential in processed:
                continue
            processed.add(new_sentential)
            queue.append(new_sentential)
        #

    return res
