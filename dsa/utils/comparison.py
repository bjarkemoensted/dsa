from typing import cast, overload

from dsa.utils.types import Comparison, Conversion


class KeyComparison[T]:
    """Helper callable for using a key function for comparing elements"""

    def __init__[C](self, relation: Comparison[C], key: Conversion[T, C]) -> None:
        self.relation = relation
        self.key = key

    def __call__(self, a: T, b: T, /) -> bool:
        return self.relation(self.key(a), self.key(b))


@overload
def make_comparison[T](relation: Comparison[T], *, key: None=..., **kwargs: object) -> Comparison[T]: ...
@overload
def make_comparison[T, C](relation: Comparison[C], *, key: Conversion[T, C], **kwargs: object) -> Comparison[T]: ...
def make_comparison[T, C](relation: Comparison[C], *, key: Conversion[T, C]|None=None, **kwargs: object) -> Comparison[T]:
    """Helper function for making a comparer callable, optionally with an intermediate function"""
    if key is None:
        return cast(Comparison[T], relation)

    return KeyComparison(relation, key)
