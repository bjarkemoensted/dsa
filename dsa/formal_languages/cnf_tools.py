from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator
from copy import deepcopy
from itertools import combinations

from dsa.formal_languages.grammar import CFG
from dsa.formal_languages.types import Nonterminal, ProductionType, SententialType


def get_useless_symbols(G: CFG) -> list[Nonterminal]:
    """Detects 'useless' symbols in the grammar, meaning nonterminals which
    do not appear in any derivation from the start symbol.
    Identifies which nonterminals are 1) reachable and 2) can produce any
    string (including the empty string)."""

    reachable: set[Nonterminal] = set()
    front: set[Nonterminal] = {G.start_symbol}

    # Determine nonterms reachable from the start symbol
    while front:
        reachable |= front
        heads = list(front)
        front = set()
        for head in heads:
            for prod in G.productions.get(head, []):
                for symbol in prod:
                    if isinstance(symbol, Nonterminal):
                        front.add(symbol)
        front -= reachable

    # Determine which of the nonterms can produce strings
    producing: set[Nonterminal] = set()
    # Keep updating until we don't detect more string-producers
    updated = True
    while updated:
        n_determined = len(producing)
        updated = False
        for head, productions in G.productions.items():
            for rhs in productions:
                # Nonterm can produce string if it can produce a string, or a string-producing nonterm
                stringmaker = any(isinstance(symbol, str) or symbol in producing for symbol in rhs) or not rhs
                if stringmaker:
                    producing.add(head)
                    producing |= {symbol for symbol in rhs if isinstance(symbol, Nonterminal)}
        updated = len(producing) != n_determined

    useful = reachable & producing
    useless = set(G.nonterminals) - useful

    return sorted(useless)


def grammar_is_cnf(G: CFG, allow_empty_string_from_start: bool=True) -> bool:
    """Determines whether a grammar is CNF.
    Following Hopcroft & Ullman, CNF is defined as:
    1) No 'useless symbols' (nonterminals that are unreachable or have no productions)
    2) Only productions rules of the forms:
        I)    A → BC
        II)   A → a
        III)  S → ε (if we allow empty strings from the start symbol)
    
    Allowing the special case where the start symbol may produce an empty string
    makes some things a bit more complicated, but allowes CNF grammars to produce empty strings.
    """
    
    # non-CNF if there are useless symbols
    useless_symbols = get_useless_symbols(G)
    if len(useless_symbols) != 0:
        return False
    
    # Check for empty productions, or rules that aren't splits (A → BC) or string productions (A → a)
    for nonterm, prods in G.productions.items():
        empty_ok = allow_empty_string_from_start and nonterm == G.start_symbol
        for p in prods:
            # Check empty
            empty = len(p) == 0

            # Check A → BC or A → a
            split = len(p) == 2 and all(isinstance(nt, Nonterminal) for nt in p)
            string_ = len(p) == 1 and all(isinstance(s, str) for s in p)

            # Check if the production has one of the three (I - III) forms allowed.
            cnf_rules_sat = split or string_ or (empty and empty_ok)
            if not cnf_rules_sat:
                return False
    
    return True

    
class SymbolGenerator:
    """Handles generating symbols.
    This is basically just to keep the logic for, given variables like X, X_1, ...,
    to be able to generate distinct names, with incrementing suffixes."""

    def __init__(self, nonterms: Iterable[Nonterminal], separator: str="_") -> None:
        """nonterms: iterable of non-terminals which we'll be renaming
        separator: string for separating a nonterminal's base name from its numeric suffix.
            e.g. 'X_1' (base name 'X', suffix 1)"""

        self.separator = separator
        # Determine the maximum suffix for each base name
        self.counts: dict[str, int] = {}
        for nt in nonterms:
            base, n = self.split(nt.name)
            n = 0 if n is None else n
            if n > self.counts.get(base, float("-inf")):
                self.counts[base] = n

    def split(self, s: str) -> tuple[str, int]:
        """Attempts to split a name into a base name and integer suffix, e.g.
        X_1 -> (X, 1).
        Returns None if no suffix, or if suffix can't be cast as integer (e.g. 'X_a')"""
        
        parts = s.split(self.separator)
        if len(parts) == 1:
            return s, 0
        
        suffix = parts[-1]
        prefix = self.separator.join(parts[:-1])
        try:
            return prefix, int(suffix)
        except ValueError:
            return s, 0

    def __call__(self, symbol: str|Nonterminal) -> Nonterminal:
        """Make a new nonterminal with a yet-unused name,
        by taking the base name for the nonterminal, incrementing
        its counter, and constructing a new Nonterminal with the resulting name
        Can also be passed a string"""
        
        s = symbol if isinstance(symbol, str) else symbol.name
        base, _ = self.split(s)
        try:
            self.counts[base] += 1
            n = self.counts[base]
            new_name = f"{base}{self.separator}{n}"
        except KeyError:
            self.counts[base] = 0
            new_name = base
        
        res = Nonterminal(new_name)

        return res


def _determine_nullable(production_rules: ProductionType) -> set[Nonterminal]:
    """Determine the nonterminals which may produce an empty strings.
    Defined as: A is nullable if it has a production A -> X_1 ... X_n where all X_i are either
        the empty production (), or
        is nullable"""

    nullable: set[Nonterminal] = set()
    changed = True

    while changed:
        changed = False
        for nt, prods in production_rules.items():
            if nt in nullable:
                continue
            
            # Check if the nonterm has any null productions
            produces_null = (all(symbol == () or symbol in nullable for symbol in p) for p in prods)
            if any(produces_null):
                nullable.add(nt)
                changed = True
    return nullable


def _inline_nullable_powerset(rule: list[SententialType], nullable: set[Nonterminal]) -> Iterator[SententialType]:
    """Given a production rule (list of RHS of a production), generates the additional productions which must be
    introduced to inline the nullable productions.
    For example, if the grammar is
        A → BB
        B → ε | c
    and we're processing the rule A -> BB, and the nullable set is {B}, this function will generate
    (B,) and ().
    This can be used to define an equivalent grammar with empty strings inlined:
        A → BB | B | ε
        B → c
    
    (BB is not yielded because it is already present.
    B is only yielded once even though it can be generated in two ways, i.e.
    by keeping the first or last instance of B)."""
    
    seen = set(rule)
    
    for p in rule:
        
        nullinds = [i for i, symbol in enumerate(p) if symbol in nullable]
        
        for n in range(1, len(nullinds)+1):
            for comb in combinations(nullinds, n):
                exclude = set(comb)
                inlined = tuple(symbol for i, symbol in enumerate(p) if i not in exclude)
                if inlined in seen:
                    continue
                seen.add(inlined)
                yield inlined


class CNFConverter:
    """Handles converting a grammar into Chomsky Normal Form.
    Conversion is implemented using the approach of Lange & Leiß (2009),
    also used on the Wikipedia page on Chomsky Normal Forms.
    Each step in the conversion is named accordingly (START, TERM, BIN, DEL, UNIT).
    As each step may modify the production rules and/or the start symbol in-place, I opted
    to make a class for holding the intermediate results and executing each step, to
    simplify the process of testing each step"""
    
    def __init__(self, start_symbol: Nonterminal, productions: ProductionType) -> None:
        self.steps: tuple[Callable[[], None], ...] = (
            self._start,
            self._term,
            self._bin,
            self._del,
            self._unit
        )

        self.start_symbol = start_symbol
        self.production_rules = deepcopy(productions)

        # Set up a renamer for when we need to introduce new nonterminals
        nonterms = {*self.production_rules.keys(), *self._produced_nts()}
        self.make_new_symbol = SymbolGenerator(nonterms=nonterms)

    def iter_prods(self) -> Iterator[tuple[Nonterminal, int, SententialType]]:
        """Helper for iterating over every individual production rule, and the rule index.
        To facilitate modification during iteration, we first extract the nonterminals and indices
        to iterate over, then do the iteration. Indices are reversed such that when using this
        iterator, it's safe to append extra production rules."""

        # Convert items to list in case we modify the underlying dict during iteration
        nt_inds = [(nt, list(reversed(range(len(prods))))) for nt, prods in self.production_rules.items()]

        for nt, inds in nt_inds:
            for i in inds:
                p = self.production_rules[nt][i]
                yield nt, i, p

    def _produced_nts(self) -> Iterator[Nonterminal]:
        """Iterate over all each nonterminal in the production RHS"""
        for _, _, p in self.iter_prods():
            for elem in p:
                if isinstance(elem, Nonterminal):
                    yield elem

    def _start(self) -> None:
        """START step - ensure no start symbols occur in any RHS productions.
        Modifies the production rules in-place and returns the new start symbol"""
        
        # If the current start symbol doesn't occur in an RHS, there's nothing to do
        if self.start_symbol not in self._produced_nts():
            return
        
        # Find a new, yet unused start symbol (retains the current if absent from all RHS)
        new_start = self.make_new_symbol(self.start_symbol)
        assert new_start not in self.production_rules
        
        # If introducing a new start symbol S_1, add a rule like S_1 -> S
        self.production_rules[new_start] = [(self.start_symbol,)]
        self.start_symbol = new_start

    def _term(self) -> None:
        """TERM step - ensure no rules have nonsolitary terminals"""
        # Make a mapping from strings to nonterminals that produce only that string
        solitary_prods = {}
        for nt, prods in self.production_rules.items():
            if len(prods) != 1:
                continue  # only look for productions of single strings
            for p in prods:
                if len(p) == 1 and all(isinstance(w, str) for w in p):
                    solitary_prods[p[0]] = nt  # register the nonterminal which produces this string
        
        # Now look for nonsolitary strings
        for nt, i, p in self.iter_prods():
            if len(p) <= 1:
                continue  # productions must have at least two symbols to make a nonsolitary string
            
            # Find the indices and values of the string productions
            string_syms = [(ind, symbol) for ind, symbol in enumerate(p) if isinstance(symbol, str)]
            if not string_syms:
                continue
            
            # Insert (new) nonterminals in place of the nonsolitary strings
            p_update = list(p)
            for ind, s in string_syms:
                # If we don't already have a nonterminal producing this string, generate a new one
                if s not in solitary_prods:
                    basename = f"N_{s}"  # choose a name like N_a for the terminal 'a'
                    new_nt = self.make_new_symbol(basename)
                    self.production_rules[new_nt] = [(s,)]
                    # Also note the nonterminal here, so we can reuse it
                    solitary_prods[s] = new_nt
                
                # Replace the string with the new nonterm, and add a new production rule like N_a -> 'a'
                p_update[ind] = solitary_prods[s]
            self.production_rules[nt][i] = tuple(p_update)

    def _bin(self) -> None:
        """BIN step - ensure no right-hand-sides have more than 2 non-terminals.
        Done by converting subsequent nonterminals into a chain of pairs of two nonterminals, e.g. converting
        A -> X_1 X_2 ... X_n
        into
        A     -> X_1 A_1
        A_1   -> X_2 A_2
        A_n-1 -> X_n-1 X_n
        """
        
        for nt, i, p in self.iter_prods():
            # Get the productions with too many nonterminals
            if sum(isinstance(elem, Nonterminal) for elem in p) <= 2:
                continue
            
            # Make sure no terminals are mixed in (should do the TERM step before this step)
            assert all(isinstance(elem, Nonterminal) for elem in p)
            
            # Remove the violating rule
            rule = self.production_rules[nt].pop(i)
            # Decompose violating rule into a chain. A_i -> X_i+1 A_i+1
            new_rules: list = []
            # We label each rule in the chain as left -> center right
            left = nt  # start with the original producing nonterminal

            # Decompose, leaving the last two nonterminals (X_n-1 and X_n)
            for ind in range(len(rule)-2):
                center = rule[ind]
                right = self.make_new_symbol(left)
                new_rules.append((left, center, right))
                left = right  # the next rule must start with the current right label
            
            # Add the final step in the chain (A_n-1 -> X_n-1 X_n)
            new_rules.append((left, rule[-2], rule[-1]))
            
            # Add the newly introduced rules to the grammar's production rules
            for left, center, right in new_rules:
                self.production_rules[left] = self.production_rules.get(left, []) + [(center, right)]

    def _del(self) -> None:
        """DEL step - ensure no nonterminals apart from the start symbol produces the empty string"""

        # First, get all nonterminals which are nullable i.e. can produce the empty string
        nullable = _determine_nullable(self.production_rules)
        
        # Add the rules needed to inline the nullable nonterminals
        for nt, prods in list(self.production_rules.items()):
            self.production_rules[nt] += _inline_nullable_powerset(prods, nullable)
        
        # Finally, remove explicit null productions, except from the start symbol
        for nt, i, p in self.iter_prods():
            if nt != self.start_symbol and p == ():
                del self.production_rules[nt][i]

    def _unit(self) -> None:
        """UNIT step - ensure no nonterminals produce a single nonterminal.
        For example, if rules like
        A -> B | b
        B -> C | a | b
        exist, we can substitute the 'bad' rule (A -> B) be replacing B with all its productions:
        A -> C | a | b
        """
        
        # Indices we must remove for each nonterminal. These point to the 'bad' productions
        inds_remove: dict[Nonterminal, set[int]] = defaultdict(set)
        # established substitutions that can be used in place of nonterminals, e.g. {B: [(C,), ('a',), ('b',)]}
        substitution_cache: dict[Nonterminal, set[SententialType]] = {}
        # Rules to add to the grammar to compensate for removing the bad ones
        rules_to_add: dict[Nonterminal, set[SententialType]] = defaultdict(set)
        
        def resolve_nonterm(B: Nonterminal) -> set[SententialType]:
            """Takes a 'bad' nonterminal (for example B in the case of A -> B).
            Returns a list of (not 'bad') sentential forms producible by B (e.g. [(C,), ('a',), ('b',)]).
            Recurses on encountering additional 'bad' nonterminals."""
            
            nonlocal substitution_cache
            res: set[SententialType] = set()
            try:
                res = substitution_cache[B]
            except KeyError:
                for p in self.production_rules[B]:
                    if len(p) == 1 and isinstance(p[0], Nonterminal):
                        res |= resolve_nonterm(p[0])
                    else:
                        res.add(p)

            return res

        # Look for bad productions
        for nt, ind, p in self.iter_prods():
            if len(p) == 1 and isinstance(p[0], Nonterminal):
                # Mark the rule's index for deletion
                inds_remove[nt].add(ind)
                # Determine what we need to substitute for the production  
                rules_to_add[nt] |= resolve_nonterm(p[0])
        
        # Remove the bad productions and add the good substitutions instead
        for nt, inds in inds_remove.items():
            keep_prods = [p for i, p in enumerate(self.production_rules[nt]) if i not in inds]
            add_prods = sorted(rules_to_add[nt] - set(keep_prods), key=repr)
            self.production_rules[nt] = keep_prods + add_prods
        
    def convert(self) -> None:
        for func in self.steps:
            func()


def chomsky_normal_form(G: CFG) -> CFG:
    """Converts a grammar into an equivalent CNF grammar."""

    converter = CNFConverter(start_symbol=G.start_symbol, productions=G.productions)
    converter.convert()
    res = CFG(start_symbol=converter.start_symbol, production_rules=converter.production_rules)

    return res
