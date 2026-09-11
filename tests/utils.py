from __future__ import annotations

import random
from uuid import uuid4


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
        self.uuid = uuid4()  # assign a unique ID to each instance, to check for stability

    @staticmethod
    def value_key(elem: NonComparable) -> int:
        """Example of a sorting key"""
        return elem.value
