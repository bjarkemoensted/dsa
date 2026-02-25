import random
import unittest

from dsa.algorithms.formal_languages import context_free
import dsa.algorithms.formal_languages.parse_trees

from ..datasets import cfg_examples


def is_producible_by_grammar(grammar, sentence):
    raise NotImplementedError  # TODO FIX


class TestCFG(unittest.TestCase):
    def setUp(self) -> None:
        self.grammars = []
        for example in cfg_examples.all_examples:
            grammar = context_free.Grammar(
                production_rules=example.productions,
                start_symbol=example.start_symbol
            )
            self.grammars.append(grammar)

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
                sentence = dsa.algorithms.formal_languages.parse_trees.produce_random_sentence(
                    grammar=grammar,
                    random_state=rs
                )

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
        ex = cfg_examples.example_illegal
        with self.assertRaises(context_free.InvalidGrammarError):
            _ = context_free.Grammar(production_rules=ex.productions, start_symbol=ex.start_symbol)
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
