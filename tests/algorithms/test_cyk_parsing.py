import random
import unittest

from dsa.algorithms.formal_languages import context_free

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
            print(grammar)
            for _ in range(20):
                prod = context_free.produce_random(
                    grammar=grammar,
                    random_state=rs
                )

                self.assertIsInstance(prod, tuple)
                for s in prod:
                    self.assertIsInstance(s, str)
                #
            #
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
