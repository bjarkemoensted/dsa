from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field, fields
from functools import singledispatchmethod
from itertools import count
from typing import Any, ClassVar, Literal, Self, TypeIs, get_args

from dsa.automata.finite_state_machine import EPSILON, NFA, Epsilon


class ParseError(Exception):
    """Custom error for when we fail to parse a Regex"""


@dataclass
class ASTBaseNode[T](ABC):
    """Base class for a node in the abstract syntax tree (AST)"""

    leaf: ClassVar[bool]

    @abstractmethod
    def children(self) -> Iterator[ASTBaseNode]:
        raise NotImplementedError

    @classmethod
    def n_args(cls) -> int:
        """Number of fields in the dataclass.
        This is used to infer the arity of operations. For example,
        the 'Union' subclass requires 2 operands, 'left', and 'right'."""

        n = len(fields(cls))
        return n

    def repr_node(self) -> str:
        return f"{self.__class__.__name__}"

    def display(self, indent: int=0) -> None:
        """Helper method for displaying the AST"""
        space = indent*' '
        print(f"{space}{self.repr_node()}")
        for child in self.children():
            child.display(indent=indent + 2)


@dataclass
class LiteralNode[T](ASTBaseNode):
    """Node for a single character in an expression"""

    leaf: ClassVar[bool] = True
    value: T

    def repr_node(self) -> str:
        return str(self.value)

    def children(self) -> Iterator[ASTBaseNode]:
        yield from ()


@dataclass
class Empty[T](ASTBaseNode):
    """Special node to represent an empty string"""

    leaf: ClassVar[bool] = True

    def repr_node(self) -> str:
        return "ε"

    def children(self) -> Iterator[ASTBaseNode]:
        yield from ()



@dataclass
class Operator(ASTBaseNode):
    """Base class for nodes that represent an operation (Kleene star, concatenation, etc)"""

    # Associate a precedence with each operation, for shunting yard algorithm
    precedence: ClassVar[int]
    leaf: ClassVar[bool] = False
    
    def __init_subclass__(cls, *, precedence: int, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        cls.precedence = precedence

    def children(self) -> Iterator[ASTBaseNode]:
        for field_ in fields(self):
            assert isinstance(field_, ASTBaseNode)
            yield field_


@dataclass
class Concat[T](Operator, precedence=2):
    """Node representing the concatenation operation, e.g. ab (implicit concatenation)"""

    left: ASTBaseNode[T]
    right: ASTBaseNode[T]

    def children(self) -> Iterator[ASTBaseNode]:
        yield from (self.left, self.right)


@dataclass
class Union[T](Operator, precedence=1):
    """Node representing the union operation, e.g. a|b"""

    left: ASTBaseNode[T]
    right: ASTBaseNode[T]

    def children(self) -> Iterator[ASTBaseNode]:
        yield from (self.left, self.right)


@dataclass
class Star[T](Operator, precedence=3):
    """Node representing the Kleene star, e.g. a*"""

    expr: ASTBaseNode[T]

    def children(self) -> Iterator[ASTBaseNode]:
        yield self.expr


@dataclass
class Plus[T](Operator, precedence=3):
    """Node representing Kleene plus, e.g. a+ (repeat at least once)"""

    expr: ASTBaseNode[T]

    def children(self) -> Iterator[ASTBaseNode]:
        yield self.expr




# Special characters for regular expressions
type SpecialChar = Literal["(", ")", "*", "|", "+"]
_special_chars = set(get_args(SpecialChar.__value__))


def is_special(char: object) -> TypeIs[SpecialChar]:
    return isinstance(char, str) and (char in _special_chars)


# Map symbols to the corresponding operator class
OPERATOR_SYMBOLS: dict[SpecialChar, type[Operator]] = {
    "*": Star,
    "|": Union,
    "+": Plus
}


class Parser[T]:
    """A regex parser. This is initialized with an expression consisting of any data type T, and
    special characters (parentheses, operations).
    It uses the shunting yard algorithm to transform the expression into postfix (reverse Polish) notation,
    consisting only of atomic nodes and operations. Then, the AST is constructed from the postfix data.
    
    Simple usage:
    ast = Parser(expr).parse()
    """

    def __init__(self, expr: Sequence[T|SpecialChar]) -> None:
        self.expr: Sequence[T|SpecialChar] = expr

        # Operators and parentheses are stored here (parentheses represented with None)
        self.operators: list[type[Operator]|None] = []

        # Output queue for postfix notation
        self.postfix: list[LiteralNode[T]|type[Operator]] = []
        self.preprocessed = False

    def _push_operator(self, operator: type[Operator]) -> None:
        """Handles operators during shunting yard algorithm.
        Moves top operators with precedence higher than the new operator to the postfix data,
        then pushes the new operator to the operator stack"""
        while (
            self.operators
            and self.operators[-1] is not None
            and self.operators[-1].precedence >= operator.precedence
        ):
            next_ = self.operators.pop()            
            assert next_ is not None
            self.postfix.append(next_)

        self.operators.append(operator)

    def to_postfix(self) -> None:
        """Converts a sequence of tokens into postfix (reverse Polish) notation.
        E.g. 'a|b' -> 'ab|'."""

        can_concatenate = False

        for i, token in enumerate(self.expr):
            if not is_special(token):
                # Normal characters go directly to the output queue
                if can_concatenate:
                    self._push_operator(Concat)

                self.postfix.append(LiteralNode(token))
            elif token == "(":
                if can_concatenate:
                    self._push_operator(Concat)
                # Store opening parentheses on the stack
                self.operators.append(None)
            elif token == ")":
                # Pop from the operator stack until we find the matching opening parenthesis
                matched = False
                while not matched:
                    if not self.operators:
                        raise ParseError(f"Unmatched right parenthesis at index {i}")
                    sym = self.operators.pop()
                    if sym is None:
                        matched = True
                    else:
                        self.postfix.append(sym)
            elif token in OPERATOR_SYMBOLS:
                self._push_operator(OPERATOR_SYMBOLS[token])

            can_concatenate = not is_special(token) or token in ("*",")",)
        
        # Put remaining operators in the output queue
        while self.operators:
            op = self.operators.pop()
            assert op is not None
            self.postfix.append(op)

        self.preprocessed = True

    def construct_ast(self) -> ASTBaseNode[T]:
        """Construct AST from postfix data"""

        # Make sure the postfix step has run
        if not self.preprocessed:
            raise RuntimeError
        stack: list[ASTBaseNode[T]] = []

        for token in self.postfix:
            # Push atomic tokens to the operand stack
            if isinstance(token, LiteralNode):
                stack.append(token)
            else:
                # When encountering an operator, pop the required operands and apply
                args = tuple(stack.pop() for _ in range(token.n_args()))
                elem = token(*reversed(args))
                stack.append(elem)

        # If the expression was valid, the stack has the AST root node as its only element
        res = stack.pop()
        if len(stack) != 0:
            raise ParseError(f"Error parsing '{self.expr} - '{len(stack)} tokens left on stack after parsing: {stack}")

        return res

    def parse(self) -> ASTBaseNode[T]:
        """Parses regex and returns the AST root node"""
        if len(self.expr) == 0:
            return Empty()
        self.to_postfix()
        res = self.construct_ast()
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
        

class Constructor[Q]:
    """Helper class for constructing an NFA from an AST.
    Instances of this class can be called with an AST to obtain the corresponding NFA.
    This works by implementing Thompson's construction, as described in
    Cooper and Torczon, section 2.7"""

    def __init__(self, node_generator: Iterator[Q]) -> None:
        """Instantiate a constructor.
        The node generator is used to generate distinct nodes for the NFA."""
        self.node_generator = node_generator

    @singledispatchmethod
    def construct_fragment[S](self, node: ASTBaseNode[S]) -> Fragment[Q, S]:
        """Construct a fragment from a given node in the AST.
        This is a dispatch method, delegating handling of each node class to its registered handlers.
        We raise an error if an unregistered node class is encountered"""
        raise NotImplementedError(f"No dispatch method registered for {node.__class__.__name__} operation")

    def empty_fragment(self) -> Fragment[Q, Any]:
        """Make an empty fragment (with no transition rules)"""
        u = next(self.node_generator)
        v = next(self.node_generator)
        res: Fragment[Q, object] = Fragment(initial_state=u, final_state=v)
        return res

    @construct_fragment.register
    def _(self, node: LiteralNode) -> Fragment:
        # Construct a fragment for a literal node
        res = self.empty_fragment()
        res.add_transition(u=res.initial_state, v=res.final_state, char=node.value)
        return res

    @construct_fragment.register
    def _(self, node: Union) -> Fragment:
        # Construct fragments for the left and right sides of the union
        left = self.construct_fragment(node.left)
        right = self.construct_fragment(node.right)

        res: Fragment = self.empty_fragment()
        res.transitions |= (left.transitions | right.transitions)

        # Run left/right in parallel - connect start and end to both
        for component in (left, right):
            res.add_transition(res.initial_state, component.initial_state)
            res.add_transition(component.final_state, res.final_state)

        return res

    @construct_fragment.register
    def _(self, node: Concat) -> Fragment:
        # Construct fragments for the left and right sides of the concatenation
        left = self.construct_fragment(node.left)
        right = self.construct_fragment(node.right)

        # Combine the two, adding an epsilon-transition from the left to the right part
        res = Fragment(
            initial_state=left.initial_state,
            final_state=right.final_state,
            transitions=left.transitions | right.transitions
        ).add_transition(u = left.final_state, v = right.initial_state)

        return res

    @construct_fragment.register
    def _(self, node: Star) -> Fragment:
        outer = self.empty_fragment()
        # Construct fragment for the inner expression (which the Kleene star repeats)
        inner = self.construct_fragment(node.expr)

        # Combine outer and inner fragment transitions
        outer.transitions |= inner.transitions

        # Make it optional to go into the inner expression at all
        outer.add_transition(outer.initial_state, inner.initial_state)
        outer.add_transition(outer.initial_state, outer.final_state)

        # At the end of the inner expression, finish, or repeat the expression
        outer.add_transition(inner.final_state, inner.initial_state)
        outer.add_transition(inner.final_state, outer.final_state)

        return outer

    @construct_fragment.register
    def _(self, node: Plus) -> Fragment:
        outer = self.empty_fragment()
        inner = self.construct_fragment(node.expr)
        outer.transitions |= inner.transitions

        # Make it mandatory to go into the inner expression
        outer.add_transition(outer.initial_state, inner.initial_state)

        # At the end of the inner expression, finish, or repeat the expression
        outer.add_transition(inner.final_state, inner.initial_state)
        outer.add_transition(inner.final_state, outer.final_state)


        return outer

    @construct_fragment.register
    def _(self, node: Empty) -> Fragment:
        res = self.empty_fragment()
        # Add an epsilon-transition from start -> accept
        res.add_transition(u=res.initial_state, v=res.final_state)
        return res

    def __call__[S](self, node: ASTBaseNode[S]) -> NFA[Q, S]:
        root_fragment = self.construct_fragment(node)
        res = _NFA_from_fragment(root_fragment)
        return res


def regex_to_NFA[S](expr: Sequence[S]) -> NFA[int, S]:
    """Convert a regular expression into an NFA"""
    
    # Get the abstract syntax tree
    ast = Parser(expr).parse()
    # Construct the NFA
    constructor = Constructor(node_generator=count())
    res = constructor(ast)
    return res
