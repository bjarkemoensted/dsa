import random
import unittest

from dsa.algorithms.formal_languages import context_free
from dsa.algorithms.formal_languages import cnf_tools
import dsa.algorithms.formal_languages.types

from ..datasets import cfg_examples


def is_producible_by_grammar(grammar, sentence):
    raise NotImplementedError  # TODO FIX


class TestCFG(unittest.TestCase):
    def setUp(self) -> None:
        self.examples = (
            cfg_examples.example_balanced,
            cfg_examples.example_empty,
            cfg_examples.example_arithmetic,
            cfg_examples.example_palindrome
        )

        self.grammars = [
            ex.grammar for ex in self.examples
        ]
        
        return super().setUp()

    def test_init(self) -> None:
        for grammar in self.grammars:
            self.assertIsInstance(grammar, context_free.Grammar)
        #
    
    def test_productions(self) -> None:
        rs = random.Random()
        rs.seed(0)
        for grammar in self.grammars:
            term_set = set(grammar.terminals)
            for _ in range(20):
                sentence = grammar.random_sentence(random_state=rs)

                self.assertIsInstance(sentence, tuple)
                for s in sentence:
                    self.assertIsInstance(s, str)
                    self.assertIn(s, term_set)
                #
            #
        #
    
    def test_ascii_repr(self):
        for grammar in self.grammars:
            s = grammar.ascii
            self.assertIsInstance(s, str)
            # Number of lines should be equal to the number of productions
            self.assertEqual(len(s.splitlines()), sum(map(len, grammar.productions.values())))
        #
    
    def test_invalid_grammar_error(self):
        # Check error when attempting to initialize a 'dead end' grammar (nonterminal with no productions)
        examples = (cfg_examples.example_illegal, cfg_examples.example_useless)
        for ex in examples:
            G = ex.grammar
            useless = context_free.get_useless_symbols(G)
            self.assertGreater(len(useless), 0)
        #
    
    def test_dead_end_exception(self):
        # Check error when attempting to initialize a 'dead end' grammar (nonterminal with no productions)
        G = cfg_examples.example_illegal.grammar

        rs = random.Random()
        rs.seed(0)
        with self.assertRaises(dsa.algorithms.formal_languages.types.DerivationError):
            _ = G.random_sentence(
                random_state=rs
            )
        #
    #


class TestCNF(unittest.TestCase):
    def setUp(self) -> None:
        self.examples = (
            cfg_examples.example_balanced,
            cfg_examples.example_empty,
            cfg_examples.example_arithmetic,
            cfg_examples.example_palindrome
        )

        self.grammars = [
            ex.grammar for ex in self.examples
        ]

    def test_useless_symbol_detection(self):
        G = cfg_examples.example_useless.grammar
        useless_symbols = context_free.get_useless_symbols(G)
        self.assertGreater(len(useless_symbols), 0)

    def test_cnf_detection(self):
        # Some example grammars and whether they're in CNF
        grammars_with_cnf_status = (
            (cfg_examples.example_arithmetic, False),
            (cfg_examples.example_balanced, False),
            (cfg_examples.example_balanced_cnf, True),
            (cfg_examples.example_empty, False),
            (cfg_examples.example_palindrome, False),
        )

        for ex, cnf in grammars_with_cnf_status:
            self.assertIs(cnf_tools.grammar_is_cnf(ex.grammar), cnf)
        #
    
    def test_cnf_conversion_retains_grammar(self):
        """Brute forces all sentences up to some length for some grammars.
        Check that the same sentences are produced after converting the grammar
        to CNF."""

        n_tokens = 10

        for G in self.grammars:
            sentences = G.brute_force_sentences(n_tokens)
            G_cnf = cnf_tools.chomsky_normal_form(G)
            sentences_cnf = G_cnf.brute_force_sentences(n_tokens)
            self.assertSetEqual(sentences, sentences_cnf)
        #
    #


# TODO CHECK MEMBERSHIP
# class TestCFGMembership(unittest.TestCase):

#     def test_all_grammars(self):
#         for grammar_name, entry in DATASET.items():
#             grammar = entry["grammar"]
#             sentences = entry["sentences"]

#             for sentence, expected in sentences:
#                 with self.subTest(grammar=grammar_name, sentence=sentence):
#                     result = is_producible_by_grammar(grammar, sentence)
#                     self.assertEqual(
#                         result,
#                         expected,
#                         msg=f"Grammar '{grammar_name}' failed for sentence {sentence}",
#                     )
#                 #
#             #
#         #
#     #


# if __name__ == "__main__":
#     unittest.main()
