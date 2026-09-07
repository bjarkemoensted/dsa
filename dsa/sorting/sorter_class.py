import operator
from functools import update_wrapper
from typing import Any, Protocol, overload

from dsa.utils.comparison import make_comparison
from dsa.utils.types import Comparable, Comparison, Conversion


class SortingFunction[**P](Protocol):
    """Matches an in-place sorting function which takes a list of some type T, along with a constraint function,
    whuch that f(a, b) is True if elements a and b are in order (e.g. operator.le for standard sorting).
    Arbitrary additional arguments are allowed, but the list and constraint function must be the first 2 arguments"""

    def __call__[T](self, A: list[T], constraint: Comparison[T], *args: P.args, **kwargs: P.kwargs) -> None: ...


class Sorter[**P]:
    """Callable for wrapping various sorting functions.
    A recurring issue for writing flexible sorting functions is to have them all accept either
    1) an iterable of comparable elements (e.g. elements for which we can immediately decide whether e.g. a <= b),
    or 2) an iterable of any type, along with a key function mapping said type into something comparable.
    This leads to a loooot of boilerplate code with ugly overloads, etc.
    The point of this class is to have a reusable helper class which accepts a list of elements of any type T,
    as well as a generic 'constraint' function f(a, b) for determining whether element a can be before element b
    in a sorted list.
    This class then contains all the necessary overloads etc in its `__call__` method, which
    takes optional arguments 'key' and 'reverse', constructing the constraint function f from that,
    and feeding it to the underlying sorting function.
    This is a bit cumbersome but means we avoid repeating the same boilerplate overloads over and over,
    and concentrate the related logic in a single place"""

    def __init__(self, inplace_sorter: SortingFunction[P]) -> None:
        self.func = inplace_sorter
        update_wrapper(self, inplace_sorter)

    @overload
    def __call__[C: Comparable](
        self,
        A: list[C],
        key: None=...,
        reverse: bool = ...,
        *args: P.args,
        **kwargs: P.kwargs
        ) -> list[C]: ...
    @overload
    def __call__[T, C](
        self,
        A: list[T],
        key: Conversion[T, C],
        reverse: bool = ...,
        *args: P.args,
        **kwargs: P.kwargs
        ) -> list[T]: ...
    def __call__(
            self,
            A: list[Any],
            key: Conversion[Any, Any]|None=None,
            reverse: bool=False,
            *args: P.args,
            **kwargs: P.kwargs
        ) -> list[Any]:

        A = [elem for elem in A]
        relation = operator.ge if reverse else operator.le
        constraint = make_comparison(relation=relation, key=key)
        self.func(A, constraint, *args, **kwargs)

        return A