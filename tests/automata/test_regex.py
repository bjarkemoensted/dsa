import re
import unittest
from itertools import product

from dsa.automata import regex

patterns = (
    '',
    'a',
    'b',
    'ab',
    'ba',
    'abc',
    'a|b',
    'ab|cd',
    'a*',
    'b+',
    #'a?',
    'a+',
    '(a)',
    '(ab)',
    '(a|b)',
    '(a|b)*',
    'a(a|b)*',
    '(ab)*',
    '(ab)+',
    'a+b',
    'a*b',
    'ab*',
)

MAX_STRING_LENGTH = 6
letters = list("abcd")
strings = [''.join(p) for k in range(MAX_STRING_LENGTH + 1) for p in product(letters, repeat=k)]


class TestRegex(unittest.TestCase):
    def test_parsing(self) -> None:
        """Check that valid regexes can be parsed to an AST"""
        for pattern in patterns:
            ast = regex.Parser(pattern).parse()
            self.assertIsInstance(ast, regex.BaseNode)

    def test_accept(self) -> None:
        """Test that converting REs into NFAs gives the same accepted/rejected strings as the built-in
        re library"""

        for pattern in patterns:
            compiled = re.compile(pattern)
            nfa = regex.regex_to_NFA(pattern)

            for s in strings:
                m = re.fullmatch(compiled, s)
                is_match = m is not None
                matched = nfa.accepts(s)
                self.assertIs(
                    matched,
                    is_match,
                    f"Check if pattern '{pattern}' matches string '{s}'."
                )
    
    def test_parser_implicit_concatenation(self) -> None:
        """Checks that the regex parser correctly inserts implicit concatenation where appropriate"""

        cases = (
            ("a", 0),
            ("ab", 1),
            ("ab*", 1),
            ("a(ab)", 2)
        )

        for pattern, n_concats in cases:
            with self.subTest(pattern=pattern):
                parser = regex.Parser(pattern)
                ast = parser.parse()
                n = sum(isinstance(node, regex.Node) and node.symbol == regex.Symbol.CONCATENATION for node in ast)
                self.assertEqual(n, n_concats, f"Error parsing {pattern}: {n} != {n_concats}")