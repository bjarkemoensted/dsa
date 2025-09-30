import random


def make_integers(n: int=100, seed=42, low=-100, high=100) -> list[int]:
        rs = random.Random()
        rs.seed(seed)
        res = [rs.randint(low, high) for _ in range(n)]
        return res
    #
