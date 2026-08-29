from itertools import product
import re
import unittest

from dsa.automata.regex import regex_to_NFA, Parser, BaseNode


patterns = (
    'a',
    'b',
    'ab',
    'ba',
    'abc',
    'a|b',
    'ab|cd',
    'a*',
    #'b+',
    #'a?',
    #'a+',
    '(a)',
    '(ab)',
    '(a|b)',
    '(a|b)*',
    'a(a|b)*',
    # '(ab)*',
    # '(ab)+',
    # 'a*b',
    # 'ab*',
)

MAX_STRING_LENGTH = 6
letters = list("abcd")
strings = [''.join(p) for k in range(MAX_STRING_LENGTH + 1) for p in product(letters, repeat=k)]


class TestRegEx(unittest.TestCase):
    def test_parsing(self) -> None:
        """Check that valid regexes can be parsed to an AST"""
        for pattern in patterns:
            ast = Parser(pattern).parse()
            self.assertIsInstance(ast, BaseNode)

    def test_accept(self) -> None:
        """Test that converting REs into NFAs gives the same accepted/rejected strings as the built-in
        re library"""

        for pattern in patterns:
            compiled = re.compile(pattern)
            nfa = regex_to_NFA(pattern)

            for s in strings:
                m = re.fullmatch(compiled, s)
                is_match = m is not None
                matched = nfa.accepts(s)
                self.assertIs(
                    matched,
                    is_match,
                    f"Compare pattern '{pattern}' against '{s}'. Expected match {is_match}, got {matched}"
                )
