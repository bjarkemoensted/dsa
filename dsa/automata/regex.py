from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import ClassVar, get_args, Iterator, Literal, Sequence, TypeIs


class ParseError(Exception):
    pass


@dataclass
class BaseNode[T](ABC):
    """Base class for a node in the abstract syntax tree (AST)"""

    leaf: ClassVar[bool]

    def __repr__(self) -> str:
        return "EYY"

    @abstractmethod
    def children(self) -> Iterator[BaseNode]:
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
        space = indent*' '
        print(f"{space}{self.repr_node()}")
        for child in self.children():
            child.display(indent=indent + 2)
        #


@dataclass
class Atom[T](BaseNode):
    """Node for a single character in an expression"""

    leaf: ClassVar[bool] = True
    value: T

    def repr_node(self) -> str:
        return str(self.value)

    def children(self) -> Iterator[BaseNode]:
        yield from ()
    #


@dataclass
class Empty[T](BaseNode):
    """Special node to represent an empty string"""

    leaf: ClassVar[bool] = True

    def repr_node(self) -> str:
        return "ε"

    def children(self) -> Iterator[BaseNode]:
        yield from ()
    #



@dataclass
class Operator(BaseNode):
    """Base class for nodes that represent an operation (Kleene star, concatenation, etc)"""

    # Associate a precedence with each operation, for shunting yard algorithm
    precedence: ClassVar[int]
    leaf: ClassVar[bool] = False
    
    def __init_subclass__(cls, *, precedence: int, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.precedence = precedence

    def children(self) -> Iterator[BaseNode]:
        for field in fields(self):
            assert isinstance(field, BaseNode)
            yield field
        #
    #


@dataclass
class Concat[T](Operator, precedence=2):
    """Node representing the concatenation operation, e.g. ab (implicit concatenation)"""

    left: BaseNode[T]
    right: BaseNode[T]

    def children(self) -> Iterator[BaseNode]:
        yield from (self.left, self.right)


@dataclass
class Union[T](Operator, precedence=1):
    """Node representing the union operation, e.g. a|b"""

    left: BaseNode[T]
    right: BaseNode[T]

    def children(self) -> Iterator[BaseNode]:
        yield from (self.left, self.right)


@dataclass
class Star[T](Operator, precedence=3):
    """Node representing the Kleene star, e.g. a*"""

    expr: BaseNode[T]

    def children(self) -> Iterator[BaseNode]:
        yield self.expr



# Special characters for regular expressions
type specialchar = Literal["(", ")", "*", "|"]
_special_chars = set(get_args(specialchar.__value__))


def is_special(char: object) -> TypeIs[specialchar]:
    return isinstance(char, str) and (char in _special_chars)


# Map symbols to the corresponding operator class
OPERATOR_SYMBOLS: dict[specialchar, type[Operator]] = {
    "*": Star,
    "|": Union
}


class Parser[T]:
    """A regex parser. This is initialized with an expression consisting of any data type T, and
    special characters (parentheses, operations).
    It uses the shunting yard algorithm to transform the expression into postfix (reverse Polish) notation,
    consisting only of atomic nodes and operations. Then, the AST is constructed from the postfix data."""

    def __init__(self, expr: Sequence[T|specialchar]) -> None:
        self.expr: Sequence[T|specialchar] = expr

        # Operators and parentheses are stored here (parentheses represented with None)
        self.operators: list[type[Operator]|None] = []

        # Output queue for postfix notation
        self.postfix: list[Atom[T]|type[Operator]] = []
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

                self.postfix.append(Atom(token))
            elif token == "(":
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

    def construct_ast(self) -> BaseNode[T]:
        """Construct AST from postfix data"""

        # Make sure the postfix step has run
        if not self.preprocessed:
            raise RuntimeError
        stack: list[BaseNode[T]] = []

        for token in self.postfix:
            # Push atomic tokens to the operand stack
            if isinstance(token, Atom):
                stack.append(token)
            else:
                # When encountering an operator, pop the required operands and apply
                args = (stack.pop() for _ in range(token.n_args()))
                elem = token(*args)
                stack.append(elem)
            #

        # If the expression was valid, the stack has the AST root node as its only element
        res = stack.pop()
        if len(stack) != 0:
            raise ParseError(f"{len(stack)} tokens left on stack after parsing")

        return res

    def parse(self) -> BaseNode[T]:
        """Parses regex and returns the AST root node"""
        if len(self.expr) == 0:
            return Empty()
        self.to_postfix()
        res = self.construct_ast()
        return res


def regex_to_ast[T](expr: Sequence[T|specialchar]) -> BaseNode[T]:
    parser = Parser(expr)

    ast = parser.parse()
    ast.display()

    return ast
    


nfa = regex_to_ast("aa|b")


regex_to_ast("(a|b)*|a")

regex_to_ast("")
