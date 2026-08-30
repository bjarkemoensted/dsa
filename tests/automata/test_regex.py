import re
import unittest
from functools import cache
from itertools import product
from typing import Sequence

from dsa.automata import regex

simple_patterns = (
    'a',
    'b',
    'ab',
    'ba',
    'abc',
    'a|b',
    'ab|cd',
    'a*b',
    'ab*',
)

parenthesis = (
    '(a)',
    '(ab)',
    '(a|b)',
    '(a|b)*',
    'a(a|b)*',
    '(ab)*',
)

more_operators = (
    'a?',
    'b*',
    'a+',
    '(ab)+',
    'a+b',
)



@cache
def make_strings(alphabet: Sequence[str]="abcd", length: int=6) -> list[str]:
    res = [''.join(p) for k in range(length + 1) for p in product(alphabet, repeat=k)]
    return res


class TestRegex(unittest.TestCase):
    def check_parsing(self, patterns: Sequence[str]) -> None:
        """Check that valid regexes can be parsed to an AST"""
        for pattern in patterns:
            ast = regex.Parser(pattern).parse()
            self.assertIsInstance(ast, regex.BaseNode)

    def compare(self, patterns: Sequence[str], alphabet: Sequence[str]="abcd", length: int=6) -> None:
        """Test that converting REs into NFAs gives the same accepted/rejected strings as the built-in
        re library"""

        self.check_parsing(patterns)

        strings = make_strings(alphabet, length)
        some_matched = False

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
                if is_match:
                    some_matched = True
                #
            #
        
        if not some_matched:
            raise RuntimeError("No strings matched any pattern.")

    def test_simple_patterns(self) -> None:
        self.compare(simple_patterns, "abcd")

    def test_empty(self) -> None:
        self.compare([""], "abc")

    def test_parentheses(self) -> None:
        self.compare(parenthesis, "ab")

    def test_more_operators(self) -> None:
        self.compare(more_operators, "ab")

    def test_escape_chars(self) -> None:
        patterns = (r"a\(b", r"ab\*", r"\\\\")
        self.compare(patterns, "ab()\\*")
    
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