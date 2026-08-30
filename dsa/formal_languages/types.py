from typing import NamedTuple, TypeGuard


class InvalidGrammarError(Exception):
    """Exception for when detecting rule violations when defining a grammar"""


class Nonterminal(NamedTuple):
    """A nonterminal.
    Storing this in a distinct class to avoid confusion with terminals (e.g. if relying on e.g. using
    upper case for nonterminals and lower case for terminals)"""

    name: str

    def __hash__(self) -> int:
        return tuple.__hash__(self)

    def __eq__(self, other: object) -> bool:
        # This is to avoid accidentally matching with a string
        return isinstance(other, Nonterminal) and tuple.__eq__(self, other)

    def __repr__(self) -> str:
        return self.name

# Types for sentences and sentential forms
type SymbolType = str|Nonterminal
type SententialType = tuple[SymbolType, ...]
type SentenceType = tuple[str, ...]

# Alias for production rules (mapping each nonterminal to a list of productions)
type ProductionType = dict[Nonterminal, list[SententialType]]


def is_sentential(obj: object) -> TypeGuard[SententialType]:
    return isinstance(obj, tuple) and all(isinstance(elem, (str, Nonterminal)) for elem in obj)


def is_sentence(obj: object) -> TypeGuard[SentenceType]:
    return isinstance(obj, tuple) and all(isinstance(elem, str) for elem in obj)
