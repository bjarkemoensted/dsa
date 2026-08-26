from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import get_args, Iterator, Literal, Sequence, TypeIs


type RegEx[T] = Atom[T] | Concat[T] | Union[T] | Star[T] | Empty[T]


class ParseError(Exception):
    pass


@dataclass
class BaseNode(ABC):

    def __repr__(self) -> str:
        return "EYY"
    
    def children(self) -> Iterator[BaseNode]:
        yield from ()

    def repr_node(self) -> str:
        return f"{self.__class__.__name__}"

    def display(self, indent: int=0) -> None:
        space = indent*' '
        print(f"{space}{self.repr_node()}")
        for child in self.children():
            child.display(indent=indent + 2)


@dataclass
class Atom[T](BaseNode):
    value: T
    def repr_node(self) -> str:
        return str(self.value)


@dataclass
class Concat[T](BaseNode):
    left: RegEx[T]
    right: RegEx[T]

    def children(self) -> Iterator[BaseNode]:
        yield from (self.left, self.right)


@dataclass
class Union[T](BaseNode):
    left: RegEx[T]
    right: RegEx[T]

    def children(self) -> Iterator[BaseNode]:
        yield from (self.left, self.right)


@dataclass
class Star[T](BaseNode):
    expr: RegEx[T]

    def children(self) -> Iterator[BaseNode]:
        yield self.expr


@dataclass
class Empty[T](BaseNode):
    pass


# Special characters for regular expressions
type specialchar = Literal["(", ")", "*", "|"]
_special_chars = set(get_args(specialchar.__value__))


def is_special(char: object) -> TypeIs[specialchar]:
    return isinstance(char, str) and (char in _special_chars)


# TODO get rid of this and just use the Node classes directly
@dataclass
class Operator:
    op: Literal["*", "|", "."]


class Parser[T]:
    PRECEDENCE: dict[str, int] = {
        "|": 1,
        ".": 2,
        "*": 3
    }

    def __init__(self, expr: Sequence[T|specialchar]) -> None:
        self.expr: Sequence[T|specialchar] = expr
        # Store operations and parentheses on a stack
        self.operators: list[Operator|Literal["("]] = []
        # Output queue for postfix notation
        self.postfix: list[T|Operator] = []
        self.preprocessed = False

    def _push_operator(self, operator: Operator) -> None:
        while (
            self.operators
            and self.operators[-1] != "("
            and self.PRECEDENCE[self.operators[-1].op] >= self.PRECEDENCE[operator.op]
        ):
            next_ = self.operators.pop()
            assert isinstance(next_, Operator)
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
                    self._push_operator(Operator("."))

                self.postfix.append(token)
            elif token == "(":
                # Store opening parentheses on the stack
                self.operators.append(token)
            elif token == ")":
                # Pop from the operator stack until we find the matching opening parenthesis
                matched = False
                while not matched:
                    if not self.operators:
                        raise ParseError(f"Unmatched right parenthesis at index {i}")
                    sym = self.operators.pop()
                    if sym == "(":
                        matched = True
                    else:
                        self.postfix.append(sym)
            elif token in self.PRECEDENCE:
                self._push_operator(Operator(token))

            can_concatenate = not is_special(token) or token in ("*",")",)
        
        # Put remaining operators in the output queue
        while self.operators:
            op = self.operators.pop()
            assert isinstance(op, Operator)
            self.postfix.append(op)

        self.preprocessed = True

    def construct_ast(self) -> RegEx[T]:
        if not self.preprocessed:
            raise RuntimeError
        stack: list[RegEx[T]] = []

        for token in self.postfix:
            if isinstance(token, Operator):
                match token.op:
                    case "*":
                        stack.append(Star(stack.pop()))
                    case "|":
                        right = stack.pop()
                        left = stack.pop()
                        stack.append(Union(left, right))
                    case ".":
                        right = stack.pop()
                        left = stack.pop()
                        stack.append(Concat(left, right))
                    case _:
                        raise ParseError(f"Invalid operator: {token.op}")
            else:
                stack.append(Atom(token))
            
        res = stack[0]
        return res

    def parse(self) -> RegEx[T]:
        self.to_postfix()
        res = self.construct_ast()
        return res


def regex_to_ast[T](expr: Sequence[T|specialchar]) -> RegEx[T]:
    parser = Parser(expr)

    ast = parser.parse()
    ast.display()

    return ast
    


nfa = regex_to_ast("aa|b")


regex_to_ast("(a|b)*|a")