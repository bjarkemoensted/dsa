import random


def make_integers(n: int=100, seed: int=42, low: int=-100, high: int=100) -> list[int]:
        rs = random.Random()
        rs.seed(seed)
        res = [rs.randint(low, high) for _ in range(n)]
        return res
