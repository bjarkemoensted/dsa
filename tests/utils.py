from __future__ import annotations

import random


def make_integers(n: int=100, seed: int=42, low: int=-100, high: int=100) -> list[int]:
    rs = random.Random()
    rs.seed(seed)
    res = [rs.randint(low, high) for _ in range(n)]
    return res


class NonComparable:
    """Example of a non-comparable class (doesn't support comparison like <= out of the box)"""

    def __init__(self, value: int, other_value: int=0) -> None:
        self.value = value
        self.other_value = other_value

    @staticmethod
    def value_key(elem: NonComparable) -> int:
        """Example of a sorting key"""
        return elem.value
