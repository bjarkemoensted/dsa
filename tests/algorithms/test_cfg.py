import random
import typing
import unittest
from collections import Counter

from dsa.formal_languages import cnf_tools
from dsa.formal_languages.cyk import CYKParser
from dsa.formal_languages.grammar import CFG
from dsa.formal_languages.parse_trees import (
    DirectionType,
    ParseNode,
    brute_force_sentences,
    grow_random_parse_tree,
)
from dsa.formal_languages.types import (
    InvalidGrammarError,
    Nonterminal,
    ProductionType,
    SententialType,
)

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
            self.assertIsInstance(grammar, CFG)
    
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
    
    def test_ascii_repr(self) -> None:
        bad_grammars = [cfg_examples.example_useless.grammar]
        grammars = list(self.grammars) + bad_grammars
        for grammar in grammars:
            s = grammar.ascii
            self.assertIsInstance(s, str)
            # Number of lines should be equal to the number of productions
            n_rules_ascii = sum(len(line.split("|")) for line in s.splitlines())
            n_rules_grammar = sum(map(len, grammar.productions.values()))
            self.assertEqual(n_rules_ascii, n_rules_grammar)
    
    def test_invalid_grammar_error(self) -> None:
        # Check error when attempting to initialize a 'dead end' grammar (nonterminal with no productions)
        ex = cfg_examples.example_illegal
        with self.assertRaises(InvalidGrammarError):
            _ = CFG(
                production_rules=ex.productions,
                start_symbol=ex.start_symbol
            )


class TestUselessSymbolDetection(unittest.TestCase):
    def test_start_symbol(self) -> None:
        """Check that the start symbol isn't mistakenly labelled as 'useless' because it's unreachable
        from other nonterms - in a CNF grammar, the start should, by construction, not be reachable from
        any nonterm, so it's crucial to allow the start symbol to act as a source node."""
        
        for ex in cfg_examples.all_examples:
            for G in (ex.grammar, cnf_tools.chomsky_normal_form(ex.grammar)):
                useless = cnf_tools.get_useless_symbols(G)
                msg = f"Example {ex.name} labelled start symbol {G.start_symbol} as useless"
                self.assertNotIn(G.start_symbol, useless, msg)


    def test_nonterm_cycle(self) -> None:
        """Check that a grammar which contains an unreachable 'cycle' (A -> B, B -> A), in which one
        of the nonterms could produce a string, is still caught as being 'useless', because the cycle
        cannot be reached"""
        
        S = Nonterminal("S")
        A = Nonterminal("A")
        B = Nonterminal("B")
        C = Nonterminal("C")

        g: ProductionType = {
            S: [(), ("a",), ("b", A)],
            A: [("x",), ()],
            B: [(C,)],
            C: [(B, "x")]
        }

        G = CFG(g, S)
        useless = set(cnf_tools.get_useless_symbols(G))
        truly_useless = {B, C}
        self.assertSetEqual(useless, truly_useless)


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

    def _partially_converted(self, last_step: str) -> typing.Iterator[CFG]:
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
            # Make sure this fails if we specify a step that doesn't exist
            if not encountered:
                raise RuntimeError(f"Didn't encounter conversion step: {last_step}")
            
            G_converted = CFG(
                start_symbol=converter.start_symbol,
                production_rules=converter.production_rules
            )

            yield G_converted

    def test_start_step(self) -> None:
        """Check that the START step has removed any RHS productions of the start symbol"""
        for G in self._partially_converted("_start"):
            for symbol in G.iter_produced_symbols():
                self.assertNotEqual(symbol, G.start_symbol)
    
    def test_term_step(self) -> None:
        """Test that the TERM step has removed any nonsolitary terminals in productions"""
        for G in self._partially_converted("_term"):
            for p in G.iter_rhs():
                n_terminals = sum(isinstance(symbol, str) for symbol in p)
                # Check that terminals make up all or none of the symbols
                self.assertIn(n_terminals, (0, len(p)))
    
    def test_bin_step(self) -> None:
        """Test that the BIN step has removed any productions of more than 2 nonterminals"""

        for G in self._partially_converted("_bin"):
            for p in G.iter_rhs():
                n_nonterms = sum(isinstance(symbol, Nonterminal) for symbol in p)
                self.assertLessEqual(n_nonterms, 2)

    def test_del_step(self) -> None:
        """Test that the DEL step has removed any empty productions except from the start symbol"""
        
        for G in self._partially_converted("_del"):
            nt_sym = ((nt, sym) for nt, prods in G.productions.items() for p in prods for sym in p)
            for nt, sym in nt_sym:
                if nt == G.start_symbol:
                    continue
                self.assertNotEqual(sym, ())

    def test_unit_step(self) -> None:
        """Test that the UNIT step has removed productions of individual nonterminals (A -> B)"""
        
        for G in self._partially_converted("_unit"):
            for p in G.iter_rhs():
                if len(p) != 1:
                    continue
                self.assertNotIsInstance(p[0], Nonterminal)

    def test_useless_symbol_detection(self) -> None:
        G = cfg_examples.example_useless.grammar
        useless_symbols = cnf_tools.get_useless_symbols(G)
        self.assertGreater(len(useless_symbols), 0)

    def test_cnf_detection(self) -> None:
        # Some example grammars and whether they're in CNF
        grammars_with_cnf_status = (
            (cfg_examples.example_arithmetic, False),
            (cfg_examples.example_balanced, False),
            (cfg_examples.example_balanced_cnf, True),
            (cfg_examples.example_empty, True),
            (cfg_examples.example_palindrome, False),
        )

        for ex, cnf in grammars_with_cnf_status:
            self.assertIs(cnf_tools.grammar_is_cnf(ex.grammar), cnf, f"CNF detection failed for '{ex.name}'")
    
    def test_cnf_conversion_retains_grammar(self) -> None:
        """Brute forces all sentences up to some length for some grammars.
        Check that the same sentences are produced after converting the grammar
        to CNF."""

        n_tokens = 10

        for G in self.grammars:
            sentences = set(G.brute_force_sentences(n_tokens))
            G_cnf = cnf_tools.chomsky_normal_form(G)
            sentences_cnf = set(G_cnf.brute_force_sentences(n_tokens))
            self.assertSetEqual(sentences, sentences_cnf)
    
    def test_cnf_after_conversion(self) -> None:
        for ex in self.examples:
            G = ex.grammar
            G_cnf = cnf_tools.chomsky_normal_form(G)
            self.assertTrue(cnf_tools.grammar_is_cnf(G_cnf), f"Example {ex.name} not CNF")


class TestCFGMembership(unittest.TestCase):
    def test_all_grammars(self) -> None:
        for ex in cfg_examples.all_examples:
            grammar_name = ex.name
            parser = CYKParser(ex.grammar)

            for sentence, producible in ex.sentences:
                with self.subTest(grammar=grammar_name, sentence=sentence):
                    result = parser.accepts(sentence)
                    self.assertEqual(
                        result,
                        producible,
                        msg=f"Grammar '{grammar_name}' failed for sentence {sentence}",
                    )


class TestParseTrees(unittest.TestCase):
    def setUp(self) -> None:
        self.examples = cfg_examples.all_examples

    def test_parse_tress_for_accepted_sentences(self) -> None:
        for ex in self.examples:
            G = ex.grammar
            parser = CYKParser(G)
            
            for sentence, accepted in ex.sentences:
                tree = parser.parse(sentence)
                self.assertIs(tree is None, not accepted, msg=f"Error in {ex.name}")

    def test_parse_forests_match_productions(self) -> None:
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
    
    def test_parse_forest_on_non_producible_sentence(self) -> None:
        for ex in self.examples:
            G = ex.grammar
            parser = CYKParser(G)
            sentence = tuple("xyzæøå")
            forest = parser.make_parse_forest(sentence)
            n = 0
            for _ in forest:
                n += 1
            self.assertEqual(n, 0)
    
    def test_parse_forest_trees_are_distinct(self) -> None:
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
    
    def _check_parse_node_grammar_consistency(
            self,
            G: CFG,
            node: ParseNode
        ) -> None:
        """Starts from an input node in a parse tre and recursively checks that parent-child relations
        are consistent with the input grammar."""
        
        # Leaf nodes must contain 1) one of the grammar's terminals or 2) correspond to epsilon
        if node.is_leaf:
            if isinstance(node.symbol, Nonterminal):
                # If nonterminal, check that empty productions are allowed
                self.assertIn((), G.productions[node.symbol])
            else:
                # Otherwise, check that the symbol is among the grammar's nonterminals
                self.assertIsInstance(node.symbol, str)
                self.assertIn(node.symbol, G.terminals)
            return

        head = node.symbol
        assert isinstance(head, Nonterminal)
        # Node must contain the start symbol iff it is the root
        if node.is_root:
            self.assertEqual(head, G.start_symbol)
        else:
            self.assertNotEqual(head, G.start_symbol)
        
        # Check that the node's children correspond to a production
        body = tuple(child.symbol for child in node.children)
        self.assertIn(body, G.productions[head])

        # Proceed to check child nodes
        for child in node.children:
            self._check_parse_node_grammar_consistency(G, child)

    def test_parse_forest_trees_respect_grammar(self) -> None:
        for ex in self.examples:
            G = ex.grammar
            parser = CYKParser(G)
            for sentence, _ in ex.sentences:
                forest = parser.make_parse_forest(sentence)
                for tree in forest:
                    self._check_parse_node_grammar_consistency(
                        G=parser.G,
                        node=tree
                    )
    
    @staticmethod
    def _find_next_nonterminal(sentential: SententialType, direction: DirectionType,) -> tuple[int, Nonterminal]|None:
        """Get the first (index, value) of a nonterminal in a sentential form, in the specified direction"""
        ind_sym = list(enumerate(sentential))

        match direction:
            case "leftmost":
                pass
            case "rightmost":
                ind_sym.reverse()
            case _:
                raise ValueError(f"Invalid direction: {direction}")
        
        for i, sym in ind_sym:
            if isinstance(sym, Nonterminal):
                return i, sym
        
        return None

    def _check_derivation(self, G: CFG, tree: ParseNode, direction: DirectionType) -> None:
        """Check that the tree derives a sentence according to grammar G."""
        steps = tree.iterate_derivation(direction=direction)
        # Derivation must start with the start symbol
        current_state = next(steps)
        self.assertTupleEqual(current_state, (G.start_symbol,))

        for next_state in steps:
            assert all(isinstance(symbol, (str, Nonterminal)) for symbol in next_state)
            expand_ind_sym = self._find_next_nonterminal(sentential=current_state, direction=direction)
            if expand_ind_sym is None:
                break
            
            expand_ind, expand_sym = expand_ind_sym
            len_diff = len(next_state) - len(current_state)
            assert len_diff >= -1

            cut_a, cut_b = expand_ind, expand_ind + len_diff + 1
            left = next_state[:cut_a]
            expanded = next_state[cut_a:cut_b]
            right = next_state[cut_b:]

            # Check new state and old state are identical except for expanded symbols
            prev_left = current_state[:expand_ind]
            prev_right = current_state[expand_ind+1:]
            prev_parts = prev_left + prev_right
            current_parts = left+right

            # E.g. if a A S b => a A a b b, (expanded S into a b) compare a A b
            self.assertTupleEqual(prev_parts, current_parts)

            self.assertIn(expanded, G.productions[expand_sym])

            current_state = next_state

    def test_derivations(self) -> None:
        for ex in self.examples:
            rs = random.Random()
            rs.seed(0)
            G = ex.grammar
            # Avoid double-checking identical trees
            already_checked: set[tuple] = set()

            for _ in range(20):
                tree = grow_random_parse_tree(
                    from_symbol=G.start_symbol,
                    productions=G.productions,
                    random_state=rs,
                    target_max_depth=20
                )

                _tree_tup = tree.as_tuple()
                if _tree_tup in already_checked:
                    continue
                already_checked.add(_tree_tup)

                for direction in ("leftmost", "rightmost"):
                    self._check_derivation(G=G, tree=tree, direction=direction)


if __name__ == "__main__":
    unittest.main()
