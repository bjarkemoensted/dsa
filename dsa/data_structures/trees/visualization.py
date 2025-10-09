from __future__ import annotations
from typing import Callable, ClassVar, Iterator, Literal, TypeAlias, TYPE_CHECKING

if TYPE_CHECKING:
    from dsa.data_structures.trees.tree import TreeNode


_default_vert = "│"
_default_bend = "└── "
_default_split = "├── "


def _default_node_representation(node: TreeNode) -> str:
    """Default way of representing a node in a tree"""
    s = repr(node.key)
    return s


class TreeRenderer:
    """Helper class for representing a tree structure as a string.
    These can be instantiated explicitly, or a few default renderers can be registered
    in a class registry for easy lookup via a style label string.
    Functions which rely on rendering trees can then accept such a label."""
    
    # Class registry for linking style 'labels' to renderers
    _registry: ClassVar[dict[str, TreeRenderer]] = dict()
    
    def __init__(
            self,
            bend: str=_default_bend,
            split: str=_default_split,
            vert: str=_default_vert,
            node_style: Callable[[TreeNode], str] | None=None
        ) -> None:
        """Make a renderer object for representing trees as strings.
        bend: string to represent an L-shaped bend
        split: string for a split connector (rotated T-shape)
        cert: string for a vertical connector(like '-')
        node_style: Optional callable for turning a node into a string"""
        
        self.bend: str = bend
        self.vert: str = vert
        self.split: str = split
        self.node_to_string = node_style or _default_node_representation
    
    @classmethod
    def register_style(cls, label: str, renderer: TreeRenderer) -> None:
        cls._registry[label] = renderer
    
    @classmethod
    def from_style(cls, label: stylelabel) -> TreeRenderer:
        """Make a renderer from one of a few predefined styles"""
        if label not in cls._registry:
            raise KeyError(f"No style labelled '{label}'.")
        
        inst = cls._registry[label]
        return inst
    
    def iterlines(self, node: TreeNode, prefix: str="", last=True, is_root=True) -> Iterator[str]:
        """Recursively iterates through nodes in a tree, considering the input node as the root of the tree.
        Lines are generated using 1) a prefix string, 2) a connector, and 3) a representation of the node.
        prefix: The current prefix.
        last: Whether the current node if the last child of its parent (defined as true for the root node)
        is_root: True only for the very first node over which we iterate. This is to avoid using a connector
            for the root node."""

        # Determine the connector (override with empty wtring for root to avoid indenting the entire tree)
        connector = self.bend if last else self.split
        if is_root:
            connector = ""
        
        node_str = self.node_to_string(node)
        s = f"{prefix}{connector}{node_str}"
        yield s
        
        # prefix for child nodes (include vertical connector except for last child)
        add_prefix = " "*len(connector) if last else self.vert+(len(connector)-1)*" "
        child_prefix = prefix + add_prefix
        
        for i, child in enumerate(node.children):        
            last_child = i == len(node.children) - 1
            yield from self.iterlines(child, child_prefix, last=last_child, is_root=False)
    
    def __call__(self, node: TreeNode) -> str:
        res = "\n".join(self.iterlines(node=node))
        return res
    #


# Register a few standard styles
_default_renderer = TreeRenderer()
_ascii_renderer = TreeRenderer(vert="|", split="+--- ", bend="'--- ")
TreeRenderer.register_style("default", _default_renderer)
TreeRenderer.register_style("ascii", _ascii_renderer)

# This can be used to type hint style labels
stylelabel: TypeAlias = Literal["default", "ascii"]
