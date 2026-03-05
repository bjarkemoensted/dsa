from collections import Counter
import random
import typing
import unittest

from dsa.algorithms.formal_languages import cnf_tools
from dsa.algorithms.formal_languages import context_free
from dsa.algorithms.formal_languages.cyk import CYKParser
from dsa.algorithms.formal_languages.types import (
    DerivationError,
    Nonterminal,
)
from dsa.algorithms.formal_languages.parse_trees import brute_force_sentences

from ..datasets import cfg_examples


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
            n_rules_ascii = sum(len(line.split("|")) for line in s.splitlines())
            n_rules_grammar = sum(map(len, grammar.productions.values()))
            self.assertEqual(n_rules_ascii, n_rules_grammar)
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
        with self.assertRaises(DerivationError):
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

    def _partially_converted(self, last_step: str) -> typing.Iterator[context_free.Grammar]:
        """Do some of the steps in converting the test grammars into CNF, stopping at the step
        with the specified name.
        This is to simplify testing that individual steps work."""
        
        for G in self.grammars:
            converter = cnf_tools.CNFConverter(
                start_symbol=G.start_symbol,
                productions=G.productions
            )

            func = getattr(converter, last_step, None)
            assert callable(func)
            encountered = False
            
            for f in converter.steps:
                f()
                if f == func:
                    encountered = True
                    break
                #
            # Make sure this fails if we specify a step that doesn't exist
            if not encountered:
                raise RuntimeError(f"Didn't encounter conversion step: {last_step}")
            
            G_converted = context_free.Grammar(
                start_symbol=converter.start_symbol,
                production_rules=converter.production_rules
            )

            yield G_converted

    def test_start_step(self):
        """Check that the START step has removed any RHS productions of the start symbol"""
        for G in self._partially_converted("_start"):
            for symbol in G.iter_produced_symbols():
                self.assertNotEqual(symbol, G.start_symbol)
            #
        #
    
    def test_term_step(self):
        """Test that the TERM step has removed any nonsolitary terminals in productions"""
        for G in self._partially_converted("_term"):
            for p in G.iter_rhs():
                n_terminals = sum(isinstance(symbol, str) for symbol in p)
                # Check that terminals make up all or none of the symbols
                self.assertIn(n_terminals, (0, len(p)))
            #
        #
    
    def test_bin_step(self):
        """Test that the BIN step has removed any productions of more than 2 nonterminals"""

        for G in self._partially_converted("_bin"):
            for p in G.iter_rhs():
                n_nonterms = sum(isinstance(symbol, Nonterminal) for symbol in p)
                self.assertLessEqual(n_nonterms, 2)
            #
        #

    def test_del_step(self):
        """Test that the DEL step has removed any empty productions except from the start symbol"""
        
        for G in self._partially_converted("_del"):
            nt_sym = ((nt, sym) for nt, prods in G.productions.items() for p in prods for sym in p)
            for nt, sym in nt_sym:
                if nt == G.start_symbol:
                    continue
                self.assertNotEqual(sym, ())
            #
        #

    def test_unit_step(self):
        """Test that the UNIT step has removed productions of individual nonterminals (A -> B)"""
        
        for G in self._partially_converted("_unit"):
            for p in G.iter_rhs():
                if len(p) != 1:
                    continue
                self.assertNotIsInstance(p[0], Nonterminal)
            #
        #

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
            sentences = set(G.brute_force_sentences(n_tokens))
            G_cnf = cnf_tools.chomsky_normal_form(G)
            sentences_cnf = set(G_cnf.brute_force_sentences(n_tokens))
            self.assertSetEqual(sentences, sentences_cnf)
        #
    #


class TestCFGMembership(unittest.TestCase):
    def test_all_grammars(self):
        for ex in cfg_examples.all_examples:
            grammar_name = ex.name
            parser = CYKParser(ex.grammar)

            for sentence, producible in ex.sentences:
                with self.subTest(grammar=grammar_name, sentence=sentence):
                    result = parser.is_producible(sentence)
                    self.assertEqual(
                        result,
                        producible,
                        msg=f"Grammar '{grammar_name}' failed for sentence {sentence}",
                    )
                #
            #
        #
    #


class TestParseForests(unittest.TestCase):
    def setUp(self) -> None:
        self.examples = cfg_examples.all_examples

    def test_parse_forests_match_productions(self):
        """Check that parse forests generate one parse tree for each
        distinct derivation of a sentence"""
        
        for ex in self.examples:
            G = ex.grammar
            parser = CYKParser(G)
            max_tokens = 6
            sentences = brute_force_sentences(
                from_symbol=G.start_symbol,
                productions=G.productions,
                only_distinct=False,
                max_tokens=max_tokens
            )

            counts = Counter(sentences)
            for sentence, multiplicity in counts.items():
                forest = parser.make_parse_forest(sentence=sentence)
                n_distinct_trees = 0
                for tree in forest:
                    sentence_reconstructed = tuple(tree.sentence())
                    self.assertEqual(sentence_reconstructed, sentence)
                    n_distinct_trees += 1
                
                msg = (
                    f"* Error in example: {ex.name} *"
                    f"Grammar {G} provided {n_distinct_trees} for sentence {sentence}."
                    f"Expected {multiplicity}."
                )
                self.assertEqual(n_distinct_trees, multiplicity, msg=msg)
            #
        #
    
    def test_parse_forest_on_non_producible_sentence(self):
        for ex in self.examples:
            G = ex.grammar
            parser = CYKParser(G)
            sentence = tuple("xyzæøå")
            forest = parser.make_parse_forest(sentence)
            n = 0
            for _ in forest:
                n += 1
            self.assertEqual(n, 0)
        #
    
    def test_parse_forest_trees_are_distinct(self):
        for ex in self.examples:
            G = ex.grammar
            parser = CYKParser(G)
            for sentence, in_grammar in ex.sentences:
                if not in_grammar:
                    continue

                trees = list(parser.make_parse_forest(sentence))
                for i in range(len(trees)):
                    for j in range(i+1, len(trees)):
                        self.assertNotEqual(trees[i], trees[j])
                    #
                #
            #
        #
    #


if __name__ == "__main__":
    unittest.main()
