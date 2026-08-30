from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from functools import singledispatchmethod
from itertools import count
from typing import Literal, Self, TypeIs, cast, get_args

from dsa.automata.finite_state_machine import EPSILON, NFA, Epsilon


class ParseError(Exception):
    """Custom error for when we fail to parse a Regex"""


# Special characters for regular expressions
type SpecialChar = Literal["(", ")", "*", "|", "+", "?"]
_special_chars = set(get_args(SpecialChar.__value__))


class Symbol(StrEnum):
    PARENTHESIS_OPEN = "("
    PARENTHESIS_CLOSE = ")"
    STAR = "*"
    PLUS = "+"
    UNION = "|"
    CONCATENATION = "·"
    QUESTION = "?"
    ESCAPE = "\\"


def is_special(char: object) -> TypeIs[SpecialChar]:
    return isinstance(char, str) and (char in _special_chars)


@dataclass(repr=False)
class Token[T]:
    """Represents a single token.
    concat_left/right: whether hte character should be auto-concatenated
        To a symbol to its left and right. For example ')' should only
        concatenate right (e.g. '(ab)c' should be parsed as 'ab' concatenated with c)
    recognize: Whether the token should be automatically recognized from an expression.
        For example, for '*' it's nice to recognize the operator easily. No symbol
        is associated with concatenation, but we still like to use a symbol to e.g. visualize
        the AST, so we use a symbol, but make no attempt to recognize it in expressions"""

    value: T
    concat_left: bool = field(default=True, kw_only=True)
    concat_right: bool = field(default=True, kw_only=True)
    recognize: bool = field(default=True, kw_only=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"


@dataclass(repr=False)
class SpecialToken(Token[str]):
    """Special token class representing tokens with special meanings"""
    pass


@dataclass(repr=False)
class OperatorToken(SpecialToken):
    """Class representing an operator token
    arity: The number of operands the operator takes (e.g. 2 for concatenation)
    precedence: The operator's precedens in the order of operations"""

    arity: int
    precedence: int

    concat_left: bool = field(default=False, kw_only=True)
    concat_right: bool = field(default=True, kw_only=True)


_specialtokens = (
    SpecialToken(Symbol.PARENTHESIS_OPEN, concat_right=False),
    SpecialToken(Symbol.PARENTHESIS_CLOSE, concat_left=False),
    OperatorToken(Symbol.UNION, 2, 1, concat_right=False),
    # Concatenation. There's no standard symbol for it, so don't attempt to read in from raw regex
    OperatorToken(Symbol.CONCATENATION, 2, 2, concat_right=False, recognize=False),
    OperatorToken(Symbol.STAR, 1, 3),
    OperatorToken(Symbol.PLUS, 1, 3),
    OperatorToken(Symbol.QUESTION, 1, 3),
)


class BaseNode[T]:
    """Represents a node in the AST"""

    def _iter_depth(self, depth: int=0) -> Iterator[tuple[BaseNode[T], int]]:
        yield self, depth
        if isinstance(self, Node):
            for child in self.children:
                yield from child._iter_depth(depth+1)

    def __iter__(self) -> Iterator[BaseNode[T]]:
        yield from (node for node, _ in self._iter_depth())

    def display(self, depth: int=0) -> None:
        for child, depth in self._iter_depth():
            prefix = "  "*depth
            print(prefix, end="")
            if isinstance(child, Node):
                print(child.symbol)
            elif isinstance(child, LeafNode):
                print(child.content)
            #

class EmptyNode(BaseNode):
    pass

@dataclass
class LeafNode[T](BaseNode[T]):
    """Leaf node in the AST. Stores the value of a single element from the input"""
    content: T


@dataclass
class Node[T](BaseNode[T]):
    """Intermediate node in the AST. Stores a symbol representing an operation, and its operands
    as child nodes."""
    symbol: str
    children: tuple[BaseNode[T], ...]


class Parser[T]:
    """A regex parser. This is initialized with an expression consisting of any data type T, and
    special characters (parentheses, operations).
    It uses the shunting yard algorithm to transform the expression into postfix (reverse Polish) notation,
    consisting only of atomic nodes and operations. Then, the AST is constructed from the postfix data.
    
    Simple usage:
    ast = Parser(expr).parse()"""

    SPECIAL_CHARS = {c.value: c for c in _specialtokens}

    def __init__(self, expr: Sequence[T|SpecialChar]) -> None:
        self.expr: Sequence[T|SpecialChar] = expr
        self.idx = 0  # Pointer to current position

        # Operators and parentheses are stored here
        self.operator_stack: list[SpecialToken] = []
        # Output queue for postfix notation
        self.token_stack: list[Token[T]|OperatorToken] = []
        # Stores nodes in the abstract syntax tree
        self.ast_nodes: list[BaseNode[T]] = []

    def peek(self) -> tuple[Token[T]|SpecialToken, int]:
        """Returns the current token in the expression, and the length to skip forward
        to reach the next one. This is to allow e.g. escape characters to work"""

        char = self.expr[self.idx]

        if char == Symbol.ESCAPE:
            escaped = cast(T, self.expr[self.idx + 1])
            return Token(escaped), 2
        if is_special(char):
            return self.SPECIAL_CHARS[char], 1
        else:
            return Token(char), 1

    def make_ast_node(self, token: Token[T]|OperatorToken) -> None:
        """Creates a new node in the AST from a token.
        This replaces the final step in the shunting yard algorithm, where elements are usually
        added to an output queue. Here, the tokens are processed as they arrive."""

        if isinstance(token, OperatorToken):
            operands = (self.ast_nodes.pop() for _ in range(token.arity))
            children = tuple(reversed(tuple(operands)))
            new_node = Node(symbol=token.value, children=children)
            self.ast_nodes.append(new_node)
        else:
            self.ast_nodes.append(LeafNode(token.value))

    @singledispatchmethod
    def process_token(self, token: Token[T]) -> None:
        self.make_ast_node(token)

    @process_token.register
    def _(self, token: OperatorToken) -> None:
        """Handles operators during shunting yard algorithm.
        Moves top operators with precedence higher than the new operator to the postfix data,
        then pushes the new operator to the operator stack"""

        # Pop operators with same or higher precedence from stack
        while self.operator_stack:
            top = self.operator_stack.pop()
            if isinstance(top, OperatorToken) and top.precedence >= token.precedence:
                self.make_ast_node(top)
            else:
                self.operator_stack.append(top)
                break

        self.operator_stack.append(token)

    def _match_bracket(self) -> None:
        """Called when we encounter a closing parenthesis in the input.
        Pop from the operator stack until an opening parenthesis is encountered"""

        while self.operator_stack:
            top = self.operator_stack.pop()
            if isinstance(top, OperatorToken):
                self.make_ast_node(top)
            elif isinstance(top, SpecialToken):
                if top.value != Symbol.PARENTHESIS_OPEN:
                    raise ValueError
                return
            else:
                raise ParseError(f"Unexpected token on operator stack: {top}")
            #
        raise ParseError(f"Couldn't match closing parenthesis at index {self.idx}")

    @process_token.register
    def _(self, token: SpecialToken) -> None:
        """Process a special token - not an operator but e.g. parentheses"""
        match token.value:
            case Symbol.PARENTHESIS_OPEN:
                self.operator_stack.append(token)
            case Symbol.PARENTHESIS_CLOSE:
                self._match_bracket()
            case _:
                raise ValueError(f"Could not process: {token}")     

    def process_expression(self) -> None:
        """Processes the expression stored in the parser.
        This runs the shunting yard algorithm, constructing AST nodes as it runs"""

        # Handle the special case of the empty expression
        if not self.expr:
            self.ast_nodes.append(EmptyNode())
            return

        attempt_concat = False
        while self.idx < len(self.expr):
            token, skip = self.peek()
            implicit_concatenation = attempt_concat and token.concat_left
            if implicit_concatenation:
                _concat_token = self.SPECIAL_CHARS[Symbol.CONCATENATION]
                self.process_token(_concat_token)

            self.process_token(token)
            attempt_concat = token.concat_right
            self.idx += skip

        while self.operator_stack:
            top = self.operator_stack.pop()
            if not isinstance(top, OperatorToken):
                raise ParseError(f"Pending token: Expected operator but got {top}")
            self.make_ast_node(top)

    def parse(self) -> BaseNode[T]:
        """Parses regex and returns the AST root node"""

        self.process_expression()

        if len(self.ast_nodes) != 1:
            raise ParseError("AST structure error")

        res = self.ast_nodes[0]
        return res


@dataclass
class Fragment[Q, S]:
    """Represents a fragment of an NFA.
    When building an NFA from an AST, we construct many smaller components of the final NFA.
    Those components have some special properties, such as only having a single final/accept state.
    Because many of the rules for combining these fragments rely on these properties, construction is greatly
    simplified by using a special class for fragments during construction, only creating an NFA after all
    components are combined"""

    initial_state: Q
    final_state: Q
    transitions: defaultdict[tuple[Q, S|Epsilon], set[Q]] = field(default_factory=lambda: defaultdict(set))

    def add_transition(self, u: Q, v: Q, char: S|Epsilon=EPSILON) -> Self:
        """Adds a transition from one state to another.
        If no character is provided, the state is inferred to be an epsilon-transition"""
        self.transitions[(u, char)].add(v)
        return self


def _NFA_from_fragment[Q, S](fragment: Fragment[Q, S]) -> NFA[Q, S]:
    """Convert a fragment into an NFA"""

    # Infer the set of states and the alphabet from the transition rules
    states = {from_ for from_, _ in fragment.transitions} | set().union(*fragment.transitions.values())
    alphabet = {char for _, char in fragment.transitions if char is not EPSILON}

    nfa = NFA(
        states=states,
        initial_state=fragment.initial_state,
        final_states={fragment.final_state,},
        alphabet=alphabet,
        transitions=dict(fragment.transitions)
    )

    return nfa
        

class Constructor[Q, S]:
    """Helper class for constructing an NFA from an AST.
    Instances of this class can be called with an AST to obtain the corresponding NFA.
    This works by implementing Thompson's construction, as described in
    Cooper and Torczon, section 2.7"""

    def __init__(self, node_generator: Iterator[Q]) -> None:
        """Instantiate a constructor.
        The node generator is used to generate distinct nodes for the NFA."""
        self.node_generator = node_generator

    def empty_fragment(self) -> Fragment[Q, S]:
        """Make an empty fragment (with no transition rules)"""
        u = next(self.node_generator)
        v = next(self.node_generator)
        res: Fragment[Q, S] = Fragment(initial_state=u, final_state=v)
        return res

    def union(self, node: Node[S]) -> Fragment[Q, S]:
        """Construct a fragment for union"""
        # Construct fragments for the left and right sides of the union
        left, right = map(self.construct_fragment, node.children)

        res: Fragment = self.empty_fragment()
        res.transitions |= (left.transitions | right.transitions)

        # Run left/right in parallel - connect start and end to both
        for component in (left, right):
            res.add_transition(res.initial_state, component.initial_state)
            res.add_transition(component.final_state, res.final_state)

        return res

    def concatenate(self, node: Node[S]) -> Fragment[Q, S]:
        """Construct a fragment for concatenation"""
        # Construct fragments for the left and right sides of the concatenation
        left, right = map(self.construct_fragment, node.children)

        # Combine the two, adding an epsilon-transition from the left to the right part
        res = Fragment(
            initial_state=left.initial_state,
            final_state=right.final_state,
            transitions=left.transitions | right.transitions
        ).add_transition(u = left.final_state, v = right.initial_state)

        return res

    def star(self, node: Node[S]) -> Fragment[Q, S]:
        """Construct a fragment for the Kleene star (repeated 0 or more times)"""
        outer = self.empty_fragment()
        # Construct fragment for the inner expression (which the Kleene star repeats)
        expr, = node.children
        inner = self.construct_fragment(expr)

        # Combine outer and inner fragment transitions
        outer.transitions |= inner.transitions

        # Make it optional to go into the inner expression at all
        outer.add_transition(outer.initial_state, inner.initial_state)
        outer.add_transition(outer.initial_state, outer.final_state)

        # At the end of the inner expression, finish, or repeat the expression
        outer.add_transition(inner.final_state, inner.initial_state)
        outer.add_transition(inner.final_state, outer.final_state)

        return outer

    def plus(self, node: Node[S]) -> Fragment[Q, S]:
        """Construct a fragment comprised of a pattern repeated once or more"""
        outer = self.empty_fragment()
        expr, = node.children
        inner = self.construct_fragment(expr)
        outer.transitions |= inner.transitions

        # Make it mandatory to go into the inner expression
        outer.add_transition(outer.initial_state, inner.initial_state)

        # At the end of the inner expression, finish, or repeat the expression
        outer.add_transition(inner.final_state, inner.initial_state)
        outer.add_transition(inner.final_state, outer.final_state)
        return outer

    def question(self, node: Node[S]) -> Fragment[Q, S]:
        """Constructs a fragment for the optional quantifier ?, e.g. 'a?' means 'a' zero or one times"""
        outer = self.empty_fragment()
        expr, = node.children
        inner = self.construct_fragment(expr)
        outer.transitions |= inner.transitions

        outer.add_transition(outer.initial_state, inner.initial_state)
        outer.add_transition(outer.initial_state, outer.final_state)
        outer.add_transition(inner.final_state, outer.final_state)

        return outer

    def empty(self) -> Fragment[Q, S]:
        """Construct a fragment to match only the empty string"""
        res = self.empty_fragment()
        # Add an epsilon-transition from start -> accept
        res.add_transition(u=res.initial_state, v=res.final_state)
        return res

    def literal(self, node: LeafNode[S]) -> Fragment[Q, S]:
        """Construct a fragment for a literal node"""
        res = self.empty_fragment()
        res.add_transition(u=res.initial_state, v=res.final_state, char=node.content)
        return res

    def construct_fragment(self, node: BaseNode[S]) -> Fragment[Q, S]:
        if isinstance(node, LeafNode):
            return self.literal(node)
        elif isinstance(node, EmptyNode):
            return self.empty()
        if not isinstance(node, Node):
            raise TypeError(f"Invalid node type: {type(node)}")

        match node.symbol:
            case Symbol.UNION:
                return self.union(node)
            case Symbol.CONCATENATION:
                return self.concatenate(node)
            case Symbol.STAR:
                return self.star(node)
            case Symbol.PLUS:
                return self.plus(node)
            case Symbol.QUESTION:
                return self.question(node)
            case _:
                raise ValueError(f"Unknown special symbol: {node.symbol!r}")
        raise NotImplementedError

    def __call__(self, node: BaseNode[S]) -> NFA[Q, S]:
        root_fragment: Fragment[Q, S] = self.construct_fragment(node)
        res = _NFA_from_fragment(root_fragment)
        return res


def regex_to_NFA[S](expr: Sequence[S]) -> NFA[int, S]:
    """Convert a regular expression into an NFA"""
    
    # Get the abstract syntax tree
    ast = Parser(expr).parse()
    # Construct the NFA
    constructor: Constructor[int, S] = Constructor(node_generator=count())
    res = constructor(ast)
    return res
