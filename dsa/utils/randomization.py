"""Tooling for randomization and stuff"""

import random

type RandomSeeder = random.Random | int | None


def make_random_state(rs: RandomSeeder) -> random.Random:
    """Helper function for turning typical ways to seed a random state into a random state object
    Returns the input if it is already a random state.
    Otherwise, instantiates a new random state and seeds with the input"""

    if isinstance(rs, random.Random):
        return rs

    res = random.Random()
    res.seed(rs)
    return res
