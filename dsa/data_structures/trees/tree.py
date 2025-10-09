from __future__ import annotations
from typing import Generic, Iterator, TypeVar


T = TypeVar("T")


class TreeError(Exception):
    """For generic tree-related errors"""
    pass

class LoopError(Exception):
    """Error for when something would cause a cycle in the tree"""
    pass


class TreeNode(Generic[T]):
    """A node in a tree structure.
    Updates to the tree structure are triggered exlusively when setting the .parent property of a note.
    Any methods that affect the tree structure, by e.g. adding a child, must trigger subsequent updates
    through setting parents of the relevant nodes. This directionality is important to avoid accidentally
    triggering an infinite recursion where adding a child and parent nodes attempt to update each other."""
    
    def __init__(self, key: T, parent: TreeNode|None=None) -> None:
        """Make a new node instance.
        key: The value stored on this node.
        parent: Optional parent node for this one."""

        self.key = key
        self._parent: TreeNode|None = None
        self.children: list[TreeNode] = []

        self.parent = parent
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.key)})"
    
    def __str__(self):
        return repr(self)
    
    @property
    def parent(self) -> TreeNode|None:
        return self._parent
    
    @parent.setter
    def parent(self, new_parent: TreeNode|None) -> None:
        """Set the parent of this node, and trigger any necessary updates to adjacent nodes"""

        # Check that setting the parent won't introduce a loop        
        if new_parent is not None and any(child is new_parent for child in self.iter_bfs()):
            raise LoopError(f"Can't set parent - {new_parent} is a descendant of {self}")

        # Remove this node from the old parent's children
        old_parent = self._parent
        if old_parent is not None:
            old_parent._unregister_child(self)
        
        # Add this node as child of new parent
        self._parent = new_parent
        if new_parent is not None:
            new_parent._register_child(self)
    
    def add_child(self, child: TreeNode) -> None:
        if any(c is child for c in self.children):
            raise TreeError(f"{child} is already a child of {self}")
        child.parent = self
    
    def remove_child(self, child: TreeNode) -> None:
        """Removes a child from this node"""
        if not any(c is child for c in self.children):
            raise TreeError(f"{child} is not a child of {self}")
        child.parent = None

    def _register_child(self, node: TreeNode) -> None:
        """Registers a new child, without triggering any other structural changes"""
        self.children.append(node)
    
    def _unregister_child(self, node: TreeNode) -> None:
        """Unregisters a child, without triggering any other structural changes"""
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
    
    def iter_dfs(self) -> Iterator[TreeNode[T]]:
        """Iterate over child nodes downwards, depth-first"""
        yield self
        for child in self.children:
            yield from child.iter_dfs()
        #
    
    def iter_bfs(self) -> Iterator[TreeNode[T]]:
        """Iterate over child nodes downwards, breadth-first"""
        queue = [self]
        next_ = []
        while queue:
            for node in queue:
                yield node
                next_.extend(node.children)
            queue = next_
            next_ = []
        #
    #
