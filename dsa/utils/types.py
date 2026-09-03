"""Stores common types used in the project"""
from typing import Any, Callable, Protocol, runtime_checkable

# Some relational comparison of 2 elements, e.g. <, >, etc
type Comparison[T] = Callable[[T, T], bool]

# Conversion from one type to another
type Conversion[T, C] = Callable[[T], C]


@runtime_checkable
class Comparable(Protocol):
    """For objects which support comparison for e.g. ordering"""

    def __lt__(self, other: Any, /) -> bool: ...
    def __le__(self, other: Any, /) -> bool: ...
    def __gt__(self, other: Any, /) -> bool: ...
    def __ge__(self, other: Any, /) -> bool: ...
    def __eq__(self, other: Any, /) -> bool: ...
