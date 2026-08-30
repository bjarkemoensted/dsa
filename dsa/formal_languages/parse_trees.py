from __future__ import annotations

import random
from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Literal, TypedDict, Unpack

import anytree  # type: ignore

from dsa.formal_languages.types import (
    Nonterminal,
    ProductionType,
    SentenceType,
    SententialType,
    SymbolType,
    is_sentence,
)

# To pass parsing direction type
type DirectionType = Literal["leftmost", "rightmost"]


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
            self.children = tuple(children)

    def ascii_tree(self) -> str:
        """Represents the tree as text"""
        s = str(anytree.RenderTree(self))
        return s

    def string(self) -> str:
        """Returns the sentence (yield) from this node as a string"""
        s = "".join(self.iterate_sentence())
        return s

    def sentence(self) -> SentenceType:
        return tuple(self.iterate_sentence())
    
    def derivation(self, direction: DirectionType|None=None) -> str:
        steps = map(str, self.iterate_derivation(direction=direction))
        res = " => ".join(steps)
        return res

    def iterate_derivation(self, direction: DirectionType|None=None) -> Iterator[SententialType]:
        """Iterate over each step in the derivation represented by the parse tree,
        starting from this node.
        Each step yields the sentential form with one additional nonterminal expanded.
        direction: "leftmost" or "rightmost": Whether to always expand the leftmost or rightmost nonterminal
            in sentential.
        """

        if direction is None:
            direction = "leftmost"

        # Maintain a list of expanded symbols, and the remaining symbols
        expanded: list[SymbolType] = []
        remaining: deque[ParseNode] = deque([self])
        yield tuple(node.symbol for node in remaining)

        while remaining:
            # Keep looking for the next node not yet expanded
            elem = remaining.popleft()
            assert isinstance(elem, ParseNode)
            if isinstance(elem.symbol, str):
                expanded.append(elem.symbol)
                continue
            
            # Expand the node into its children
            extend_elems = list(elem.children)
            if direction == "leftmost":
                # Keep remaining in normal order if leftmost, reverse order if rightmost
                extend_elems.reverse()
            
            remaining.extendleft(extend_elems)

            # Generate the sentential form after the expansion. Reverse order if rightmost
            intermediate = expanded + [node.symbol for node in remaining]
            if direction == "rightmost":
                intermediate.reverse()
            
            sentential = tuple(intermediate)
            yield sentential

    def iterate_sentence(self) -> Iterator[str]:
        """Iterates over the sentence produced from this node."""

        if isinstance(self.symbol, Nonterminal):
            # For nonterminals, continue iterating over child nodes
            for child in self.children:
                yield from child.iterate_sentence()
            
        elif isinstance(self.symbol, str):
            # For terminals, just use the node's symbol
            assert self.is_leaf
            yield self.symbol
        else:
            raise TypeError

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ParseNode):
            return NotImplemented
        
        # Require the other node to hold the same symbol, and have same number of children
        nodes_differ = self.symbol != other.symbol or len(self.children) != len(other.children)
        if nodes_differ:
            return False
        
        # Recurse equality check on child nodes
        return all(child == otherchild for child, otherchild in zip(self.children, other.children))

    def __repr__(self) -> str:
        return repr(self.symbol)
    
    def as_tuple(self) -> tuple:
        return (self.symbol, tuple(c.as_tuple() for c in self.children))


def grow_random_parse_tree(
        from_symbol: Nonterminal|str,
        productions: ProductionType,
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
    options = productions[from_symbol]
    weights = [1.0 for _ in options]

    # If we're exceeding the target depth, choose only among terminal productions, if any
    if depth >= target_max_depth:
        all_terms = [all(isinstance(elem, Nonterminal) for elem in opt) for opt in options]
        if any(all_terms):
            weights = [int(at) for at in all_terms]

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
        productions: ProductionType,
        depth: int=0,
        **kwargs: Unpack[GenKwargs]
    ) -> SentenceType:
    """Produce a random sentence using the specified grammar.
    See grow_random_parse_tree docstring for details."""

    root = grow_random_parse_tree(
        from_symbol=from_symbol,
        productions=productions,
        depth=depth,
        **kwargs
    )

    res = tuple(root.iterate_sentence())
    return res


def determine_length_bounds(productions: ProductionType) -> dict[Nonterminal, int]:
    """Takes production rules and returns a dict mapping each nonterminal to a lower bound
    on the number of terminals in sentences it may produce"""
    min_lengths = {nt: float("inf") for nt in productions}
    changed = True
    while changed:
        changed = False
        for nt, prods in productions.items():
            bounds = [[1 if isinstance(symbol, str) else min_lengths[symbol] for symbol in p] for p in prods]
            new_min = min(map(sum, bounds))
            if new_min != min_lengths[nt]:
                min_lengths[nt] = new_min
                changed = True

    res = {nt: int(bound) for nt, bound in min_lengths.items()}
    return res


def brute_force_sentences(
        from_symbol: Nonterminal,
        productions: ProductionType,
        max_tokens: int,
        only_distinct: bool=True
    ) -> Iterator[SentenceType]:
    """Computes all sentences with length no greater than the specified
    number of tokens.
    from_symbol (Nonterminal): The symbol from which to start producing
    productions: the production rules (dict mapping nonterminals to tuples of Nonterminals/strings)
    max_tokens: The maximum number of symbols with which to produce sentences
    only_distinct: If true, only returns each distinct sentence once, with no double counting"""
    
    lower_bounds = determine_length_bounds(productions)
    already_produced: set[SentenceType] = set()
    queue: list[SententialType] = [(from_symbol,)]
    processed: set[SententialType] = set(queue)
    
    while queue:
        
        current = queue.pop()
        # Stop if the allowed number of tokens exceeds/will exceed target
        sentence_lower_bound = sum(1 if isinstance(elem, str) else lower_bounds[elem] for elem in current)
        if sentence_lower_bound > max_tokens:
            continue
        
        # Add sentences to results
        if is_sentence(current):
            use_sentence = not (only_distinct and current in already_produced)
            if use_sentence:
                yield current
                already_produced.add(current)
            continue
        
        # Select a random nonterminal
        ind_nts = [(i, s) for i, s in enumerate(current) if isinstance(s, Nonterminal)]
        replace_ind, symbol = random.choice(ind_nts)

        # Replace the nonterminal with all possible productions
        for rhs in productions[symbol]:
            new_sentential = (
                *current[:replace_ind],  # symbols left of the non-terminal
                *rhs,  # symbols produced by this non-terminal
                *current[replace_ind+1:]  # symbols right of the non-terminal
            )
            # If this sentential form is new, add to queue
            skip_sentential = only_distinct and (new_sentential in processed)
            if skip_sentential:
                continue
            processed.add(new_sentential)
            queue.append(new_sentential)


@dataclass
class ParseForestNode:
    """Represents a parse forest, which stores a compact representation of
    every possible parse tree for a given sentence, given a CNF grammar.
    Each node in the forest contains information on a nonterminal, and a part of the
    sentence which can be produced by a binary rule A -> BC.
        
    The node stores a list of tuples of childnodes, indicating which nonterminals B and C
    may produce a left and a right part of the sentence.
    As such, the parse forest encodes the same structure as the CYK parser discovers.
    
    Since all productions in a CNF grammar are one of
        A -> BC
        A -> a
        S -> ε
    We can check if a node is a leaf by checking whether it encodes a substring shorter
    than 2 characters.
    
    The node stores
    A: Pointer to the nonterminal producing part of the sentence
    start: The starting index for the part of the sentence
    length: The length of the part of the sentence
    nonterminals: A reference to the grammar's nonterminal (so we can just store an index at each node)
    sentence: The full sentence being parsed
    alternatives: List of tuples (left, right) of parse nodes representing substrings
        into which we can partition the remaining sentence.
    
    The parse forest mainly serves to facilitate iteration over possible parse trees.
    It implements iteration directly, i.e.
    for tree in parse_forest_instance:
        ...

    In cases where the sentence cannot be produced by the grammar, the parse forest
    is empty, and iterating will give nothing."""

    A: int
    start: int
    length: int
    nonterminals: tuple[Nonterminal, ...]
    sentence: SentenceType
    alternatives: list[tuple[ParseForestNode, ParseForestNode]] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        """Leaf node check."""
        return self.length <= 1

    def generate_parse_trees(self, parent: ParseNode|None=None) -> Iterator[ParseNode]:
        """Iterates over all possible parse trees from the current node.
        This follows a recursive approach similar to constructing a tree, with one exception:
        Because ParseForestNodes only encode nonterminal rules like A -> BC, string productions like
        A -> a are handled separately, i.e. rather than storing string productions as leaf nodes,
        and checking immediately after recursing whether a leaf has been reached, we instead
        have to check before recursing whether all there's left to do is produce a (possibly empty) string,
        and, in that case, attach a string child node to the parse tree"""
        
        nonterm = self.nonterminals[self.A]
        
        if self.is_leaf:
            # We've reached a production like A -> 'a'. Make a node for <parent> -> A
            node = ParseNode(symbol=nonterm, parent=parent)
            if self.length == 1:
                # If the production is not the empty string, add a child node for a
                ParseNode(symbol=self.sentence[self.start], parent=node)
            yield node
            return
        else:
            # Recurse on the subtrees for B and C
            for left, right in self.alternatives:
                for lefttree in left.generate_parse_trees(parent=None):
                    for righttree in right.generate_parse_trees(parent=None):
                        node = ParseNode(nonterm, children=(lefttree, righttree))
                        yield node


@dataclass
class ParseForest:
    """Wrapper for parse forests.
    This is to allow a similar interface for 'empty' forests, representing
    cases where no parse tree exists. Use None as root for an empty forest."""

    root: ParseForestNode|None

    def __iter__(self) -> Iterator[ParseNode]:
        """Iterator over all parse trees"""
        if self.root is None:
            return iter(())
        
        return iter(self.root.generate_parse_trees())
