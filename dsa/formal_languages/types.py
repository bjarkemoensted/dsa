from typing import NamedTuple, TypeAlias, TypeGuard


class InvalidGrammarError(Exception):
    """Exception for when detecting rule violations when defining a grammar"""
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

# Types for sentences and sentential forms
symboltype: TypeAlias = str|Nonterminal
sententialtype: TypeAlias = tuple[symboltype, ...]
sentencetype: TypeAlias = tuple[str, ...]

# Alias for production rules (mapping each nonterminal to a list of productions)
productiontype: TypeAlias = dict[Nonterminal, list[sententialtype]]


def is_sentential(obj) -> TypeGuard[sententialtype]:
    return isinstance(obj, tuple) and all(isinstance(elem, (str, Nonterminal)) for elem in obj)


def is_sentence(obj) -> TypeGuard[sentencetype]:
    return isinstance(obj, tuple) and all(isinstance(elem, str) for elem in obj)
