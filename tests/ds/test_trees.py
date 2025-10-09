from __future__ import annotations
import anytree  # type: ignore
import random
from typing import get_args, Optional, overload
import unittest

from dsa.data_structures.trees import tree
from dsa.data_structures.trees import visualization


def _make_nodes() -> tree.TreeNode:
    nodes = [tree.TreeNode(c) for c in "abcde"]
    for i in range(1, len(nodes)):
        nodes[i].parent = nodes[i-1]

    a, b, c, d, e = nodes
    c.parent = a
    tree.TreeNode(key=42, parent=c)
    tree.TreeNode("label", parent=c)
    return a


class NodeTest(unittest.TestCase):
    def setUp(self):
        node = _make_nodes()
        
        self.root_node = node.find_root()
    
    def test_rendering(self):
        styles = get_args(visualization.stylelabel)
        
        # Check all style labels allowed by the type hint have a registered renderer
        for style in styles:
            renderer = visualization.TreeRenderer.from_style(style)
            s = renderer(self.root_node)
            self.assertIsInstance(s, str)
            # Check that all nodes appear in the rendered tree
            keys = (node.key for node in self.root_node.iter_dfs())
            for key in keys:
                self.assertIn(str(key), s)
        
        # Check that all registered renderers are allowed by the type hint
        styles_type_hint = sorted(styles)
        styles_registry = sorted(visualization.TreeRenderer._registry.keys())
        self.assertEqual(styles_type_hint, styles_registry)
    #

    def test_iteration(self):
        dfs = set(self.root_node.iter_dfs())
        bfs = set(self.root_node.iter_bfs())
        self.assertEqual(dfs, bfs)
    #


# Map exceptions from anytree to exceptions thrown here
_exception_mapping = {
    anytree.node.exceptions.TreeError: tree.TreeError,
    anytree.node.exceptions.LoopError: tree.LoopError,
}


class WrappedNode(anytree.Node):
    """Wrapper class for anytree nodes to have attributes with the same name this library"""

    children: tuple[WrappedNode, ...]

    @property
    def key(self):
        return self.name
    
    def add_child(self, child: WrappedNode) -> None:
        self.children += (child,)
    
    def remove_child(self, child: WrappedNode) -> None:
        new_children = tuple(c for c in self.children if c is not child)
        self.children = new_children


class AnytreeComparisonTest(unittest.TestCase):
    """Tests the node tree class against the existing anytree library.
    This works by initializing two identical trees in both frameworks,
    then running a lot of randomized operations on the graph structure of both trees,
    and checking that the trees exhibit similar behavior, i.e. they maintain identical
    graph structures, and raise errors in the same cases."""

    n_nodes = 100
    rs: random.Random
    seed = 0
    nodes: list[tree.TreeNode]
    anynodes: list[WrappedNode]

    def setUp(self):
        self.rs = random.Random()
        self.rs.seed(self.seed)
        self.inds = list(range(self.n_nodes))
        # Setup nodes for both frameworks
        self.nodes = [tree.TreeNode(key=val) for val in self.inds]
        self.anynodes = [WrappedNode(val) for val in self.inds]

        assert len(self.inds) == len(self.nodes) == len(self.anynodes) == self.n_nodes

    @overload
    def randind(self, n: None=...) -> int: ...
    @overload
    def randind(self, n: int) -> tuple[int, ...]: ...
    def randind(self, n: Optional[int]=None) -> int|tuple:
        """Returns 1 or more random indices.
        If n is not specified, returns a single index, as an int.
        Otherwise, returns a tuple of n indices (samples without replacement)."""

        if n is None:
            return self.rs.choice(self.inds)

        if n > len(self.inds):
            raise ValueError
        
        inds = [i for i in self.inds]
        self.rs.shuffle(inds)

        res = tuple(inds[:n])
        return res

    def check_tree_structure(self):
        """Checks if the trees are similar in structure.
        Iterates over all nodes and compares their values in both trees, then
        compares values of parents and children."""

        for i in range(self.n_nodes):
            a = self.anynodes[i]
            b = self.nodes[i]
            
            # Compare nodes directly
            self.assertEqual(a.key, b.key)

            # Compare parents
            if a.parent is None:
                self.assertIsNone(b.parent)
            else:
                self.assertIsNotNone(b.parent, msg=f"{b} should have {a.parent.key} as parent, but has None")
                assert b.parent
                self.assertEqual(a.parent.key, b.parent.key)
            
            # Compare children
            self.assertEqual(len(a.children), len(b.children))
            for ka, kb in zip(*(sorted(c.key for c in n.children) for n in (a, b))):
                self.assertEqual(ka, kb)
            #
        #

    def _set_random_parent(self) -> None:
        """Attempts to set a random node as parent of another node"""
        
        child_ind, parent_ind = self.randind(n=2)
        try:
            self.anynodes[child_ind].parent = self.anynodes[parent_ind]
        except anytree.node.exceptions.LoopError as e:
            # If anytree won't allow the parent due to cycle creation, expect an error
            exc = _exception_mapping[type(e)]
            with self.assertRaises(exc, msg=f"anytree version failed with: {str(e)}"):
                self.nodes[child_ind].parent = self.nodes[parent_ind]
            return
        self.nodes[child_ind].parent = self.nodes[parent_ind]
    
    def _remove_random_parent(self) -> None:
        """Attempts to remove the parent of a random node"""
        ind = self.randind()
        self.anynodes[ind].parent = None
        self.nodes[ind].parent = None

    def _set_random_child(self) -> None:
        """Attempts to set a random node as child of another node"""
        child_ind, parent_ind = self.randind(n=2)
        try:
            self.anynodes[parent_ind].add_child(self.anynodes[child_ind])
        except (anytree.node.exceptions.TreeError, anytree.node.exceptions.LoopError) as e:
            exc = _exception_mapping[type(e)]
            with self.assertRaises(exc, msg=f"anytree version failed with: {str(e)}"):
                self.nodes[parent_ind].add_child(self.nodes[child_ind])
            return
        
        self.nodes[parent_ind].add_child(self.nodes[child_ind])

    def _remove_random_child(self) -> None:
        """Attempts to remove a random child from a random node."""

        all_child_inds = [i for i, c in enumerate(self.anynodes) if c.parent is not None]
        # Nothing to do if no nodes have any children
        if not all_child_inds:
            return

        # Determine a random node and its parent
        child_ind = self.rs.choice(all_child_inds)
        child = self.anynodes[child_ind]
        parent_ind = next(i for i, n in enumerate(self.anynodes) if n is child.parent)

        # Remove the child nodes
        self.anynodes[parent_ind].remove_child(self.anynodes[child_ind])
        self.nodes[parent_ind].remove_child(self.nodes[child_ind])

    def test_manipulations(self):
        """Do a series of random tree manipulations"""

        # Some random manipulations
        operations = (
            self._set_random_parent,
            self._remove_random_parent,
            self._set_random_child,
            self._remove_random_child,
        )
        # Be more hesitant to remove connections to ensure the trees don't stay too simple
        weights = [1, 0.1, 1, 0.2]
        
        # Check the trees start out similar
        self.check_tree_structure()

        for _ in range(1000):
            f = self.rs.choices(operations, weights=weights)[0]
            f()
            self.check_tree_structure()
        #
    #


if __name__ == "__main__":
    unittest.main()
