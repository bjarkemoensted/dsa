class Sentinel:
    """Sentinel class for representing various special values.
    In many circumstances, we need some value that represents some special meaning, and needs
    to be different from a set of other values. Sometimes, None is used to represent special values,
    but to allow appplications to use arbitrary types (for example for the alphabets of automata),
    there's a challenge of discerning a special value from a normal one.
    The purpose of this class is to have a dedicated class, which can be presumed to never represent
    a normal value.
    A sentinel can be initialized with an optional label, which affects how it is displayed.
    The intended usage is to create a single instance of a Sentinel to represent each kind of special
    value, then refer to that in applications (for example, a single instance referring to the empty string
    for automata)."""

    def __init__(self, label: str|None=None) -> None:
        self.label = label

    def __repr__(self) -> str:
        res = self.label if self.label is not None else "<SENTINEL>"
        return res

    def __str__(self) -> str:
        return repr(self)
