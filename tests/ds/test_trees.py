from typing import get_args
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


class QueueTest(unittest.TestCase):
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
            for node in self.root_node.iter_down():
                self.assertIn(str(node.key), s)
        
        # Check that all registered renderers are allowed by the type hint
        styles_type_hint = sorted(styles)
        styles_registry = sorted(visualization.TreeRenderer._registry.keys())
        self.assertEqual(styles_type_hint, styles_registry)
    #
