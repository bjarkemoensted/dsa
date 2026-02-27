from __future__ import annotations
import random
from typing import Iterable, Iterator

import anytree  # type: ignore

from dsa.algorithms.formal_languages.context_free import (
    Grammar
)
from dsa.algorithms.formal_languages.types import DerivationError, Nonterminal


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
        grammar: Grammar,
        random_state: random.Random|int|None=None,
        from_symbol: Nonterminal|str|None=None,
        parent: ParseNode|None=None,
        depth: int=0,
        target_max_depth=20
    ) -> ParseNode:
    """Produce a parse tree for a random sentence using the specified grammar.
    grammar: The grammar to use
    random_state: Either a random.Random instance, or int/None to be used as seed.
    from_symbol: The nonterminal to use for producing. Defaults to the start symbol.
    depth: current recursion depth.
    target_max_depth: Approximate max recusion depth desired. When exceeded, productions leading to terminals
        will be selected over nonterminals.
    """
    
    # Create a node in the parse tree
    from_symbol = grammar.start_symbol if from_symbol is None else from_symbol
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
        options = grammar.productions[from_symbol]
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
            grammar=grammar,
            random_state=random_state,
            from_symbol=elem,
            parent=node,
            depth=depth+1,
            target_max_depth=target_max_depth
        )

    return node


def produce_random_sentence(
        grammar: Grammar,
        random_state: random.Random|int|None=None,
        depth: int=0,
        target_max_depth=20
    ) -> tuple[str, ...]:
    """Produce a random sentence using the specified grammar.
    See grow_random_parse_tree docstring for details."""

    root = grow_random_parse_tree(
        grammar=grammar,
        random_state=random_state,
        depth=depth,
        target_max_depth=target_max_depth
    )

    res = tuple(root.iter_sentence())
    return res