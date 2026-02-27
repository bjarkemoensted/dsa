from typing import NamedTuple, TypeAlias


class InvalidGrammarError(Exception):
    """Exception for when detecting rule violations when defining a grammar"""
    pass


class DerivationError(Exception):
    """Exception for when unable to continue deriving a sentence"""
    pass


class Nonterminal(NamedTuple):
    """A nonterminal.
    Storing this in a distinct class to avoid confusion with terminals (e.g. if relying on e.g. using
    upper case for nonterminals and lower case for terminals)"""

    name: str

    def __hash__(self):
        return tuple.__hash__(self)

    def __eq__(self, other):
        # This is to avoid accidentally matching with a string
        return isinstance(other, Nonterminal) and tuple.__eq__(self, other)

    def __repr__(self):
        return self.name
    #


# Alias for production rules (mapping each nonterminal to a list of productions)
productiontype: TypeAlias = dict[Nonterminal, list[tuple[Nonterminal|str, ...]]]
