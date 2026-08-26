from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import ClassVar, get_args, Iterator, Literal, Sequence, TypeIs


class ParseError(Exception):
    pass


@dataclass
class BaseNode[T](ABC):
    leaf: ClassVar[bool]

    def __repr__(self) -> str:
        return "EYY"

    @abstractmethod
    def children(self) -> Iterator[BaseNode]:
        raise NotImplementedError

    @classmethod
    def n_args(cls) -> int:
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
    leaf: ClassVar[bool] = True
    value: T

    def repr_node(self) -> str:
        return str(self.value)

    def children(self) -> Iterator[BaseNode]:
        yield from ()
    #


@dataclass
class Empty[T](BaseNode):
    leaf: ClassVar[bool] = True

    def repr_node(self) -> str:
        return "ε"

    def children(self) -> Iterator[BaseNode]:
        yield from ()
    #



@dataclass
class Operator(BaseNode):
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
    left: BaseNode[T]
    right: BaseNode[T]

    def children(self) -> Iterator[BaseNode]:
        yield from (self.left, self.right)


@dataclass
class Union[T](Operator, precedence=1):
    left: BaseNode[T]
    right: BaseNode[T]

    def children(self) -> Iterator[BaseNode]:
        yield from (self.left, self.right)


@dataclass
class Star[T](Operator, precedence=3):
    expr: BaseNode[T]

    def children(self) -> Iterator[BaseNode]:
        yield self.expr



# Special characters for regular expressions
type specialchar = Literal["(", ")", "*", "|"]
_special_chars = set(get_args(specialchar.__value__))


def is_special(char: object) -> TypeIs[specialchar]:
    return isinstance(char, str) and (char in _special_chars)


OPERATOR_SYMBOLS: dict[specialchar, type[Operator]] = {
    "*": Star,
    "|": Union
}


class Parser[T]:

    def __init__(self, expr: Sequence[T|specialchar]) -> None:
        self.expr: Sequence[T|specialchar] = expr
        # Store operations and parentheses on a stack
        self.operators: list[type[Operator]|None] = []  # None represents opening brackets '('

        # Output queue for postfix notation
        self.postfix: list[Atom[T]|type[Operator]] = []
        self.preprocessed = False

    def _push_operator(self, operator: type[Operator]) -> None:
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
        if not self.preprocessed:
            raise RuntimeError
        stack: list[BaseNode[T]] = []

        for token in self.postfix:
            if isinstance(token, Atom):
                stack.append(token)
            else:
                args = (stack.pop() for _ in range(token.n_args()))
                elem = token(*args)
                stack.append(elem)
            #

        res = stack.pop()
        
        if len(stack) != 0:
            raise ParseError(f"{len(stack)} tokens left on stack after parsing")
        return res

    def parse(self) -> BaseNode[T]:
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
