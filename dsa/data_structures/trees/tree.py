from __future__ import annotations
from typing import Generic, Iterator, TypeVar


T = TypeVar("T")


def iterate_depth_and_nodes(seed: TreeNode) -> Iterator[tuple[int, TreeNode]]:
    current = [seed]
    depth = 0
    next_ = []
    while current:
        for node in current:
            yield depth, node
            next_ += node.children
        
        current = next_
        next_ = []
        depth += 1


class TreeNode(Generic[T]):
    def __init__(self, key: T, parent: TreeNode|None=None) -> None:
        self.key = key
        self._parent = None
        self.parent = parent
        self.children: list[TreeNode] = []
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.key})"
    
    def __str__(self):
        return repr(self)
    
    @property
    def parent(self) -> TreeNode|None:
        return self._parent
    
    @parent.setter
    def parent(self, new_parent: TreeNode|None) -> None:
        # Remove this node from the old parent's children
        old_parent = self._parent
        if old_parent is not None:
            old_parent._unregister_child(self)
        
        # Add this node as child of new parent
        self._parent = new_parent
        if new_parent is not None:
            new_parent._register_child(self)
    
    def _register_child(self, node: TreeNode) -> None:
        self.children.append(node)
    
    def _unregister_child(self, node: TreeNode) -> None:
        for i in reversed(range(len(self.children))):
            if self.children[i] is node:
                del self.children[i]
            #
        #
    
    @property
    def is_root(self) -> bool:
        return self._parent is None
    
    def find_root(self) -> TreeNode:
        node = self
        while node._parent:
            node = node._parent
        
        return node
    
    def render_ascii(self, indentation=2) -> None:
        # TODO need to use ├ for first n-1 children, └ for last. ─
        for depth, node in iterate_depth_and_nodes(self):
            prefix = "├" + (indentation*depth - 1)*"─"
            s = f"{prefix} {node.key}"
            print(s)
        #
    #


