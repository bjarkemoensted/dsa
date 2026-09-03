
from dsa.utils.types import Comparison, Conversion


class KeyComparison[T]:
    """Helper callable for using a key function for comparing elements"""

    def __init__[C](self, relation: Comparison[C], key: Conversion[T, C]) -> None:
        self.relation = relation
        self.key = key

    def __call__(self, a: T, b: T, /) -> bool:
        return self.relation(self.key(a), self.key(b))
