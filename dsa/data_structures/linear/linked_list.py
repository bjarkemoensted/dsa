from __future__ import annotations
from typing import (
    cast,
    Generic,
    Iterator,
    Self
)

from dsa.data_structures.linear.queue import BaseContainer, T


class Node(Generic[T]):
    """A node in a linked list.
    The value stored in the node is the key attribute.
    prev and next attributes point to the predessesor and successor nodes, respectively."""

    def __init__(self, key: T|None) -> None:
        """Initialize a node. If key is not provided, None is used initially.
        prev and next initially point to None - successor and predesssesor nodes
        must be set after initialization"""
        self.key: T|None = key
        self.prev: Node|None = None
        self.next: Node|None = None

    @classmethod
    def make_nil(cls) -> Self:
        """Makes a sentinel node to represent NIL"""
        inst = cls(key=None)
        inst.prev = inst
        inst.next = inst
        return inst
    
    def __repr__(self):
        return f"{self.__class__.__name__} <{self.key}>"
    
    def __str__(self):
        return repr(self)
    #

    def _iterate_direction(self, forward=True) -> Iterator[Node]:
        """Iterates over this node and all successors (if forward is True) or predessesors.
        Stops iteration if we run out of nodes, or if we arrive back at the starting node."""
        
        node = self
        while node:
            yield node
            next_node = node.next if forward else node.prev
            if not next_node or next_node is self:
                break
            node = next_node
        #
    #

    def forward(self) -> Iterator[Node]:
        """Iterates over this node and all successors"""
        yield from self._iterate_direction(forward=True)
    
    def backwards(self) -> Iterator[Node]:
        """Iterates over this node and all predessesor"""
        yield from self._iterate_direction(forward=False)
    #


class LinkedList(BaseContainer, Generic[T]):
    """A linked list, where elements are stored with references to the next and previous elements.
    Uses a sentinel node to represent the beginning and end of the list.
    As the number of elements can't be efficiently computed without traversing the entire list,
    a counter is maintained when attaching new nodes or detaching current ones."""
    
    def __init__(self, maxsize = -1) -> None:
        super().__init__(maxsize)
        self.nil: Node = Node.make_nil()
        self._n_elems: int = 0
    
    def _put(self, item: T):
        x = Node(key=item)
        self.attach_node(x)
    
    @property
    def head(self) -> Node:
        """The head (first node) in the list"""
        return cast(Node, self.nil.next)
    
    @property
    def tail(self) -> Node:
        """The tail (last node) in the list"""
        return cast(Node, self.nil.prev)

    def attach_node(self, node: Node, insert_after: Node|None=None) -> None:
        """Inserts a new node into the linked list.
        If insert_after is provided, the new node is inserted following the specified node.
        If not provided, the new node is inserted at the end of the list, and thus becomes the
        new tail."""
        
        # Determine the nodes which must come before and after the newly inserted node
        prev_ = insert_after or self.tail
        next_ = cast(Node, prev_.next)
        
        # Point to the new node from the neighbors in the list
        prev_.next = node
        next_.prev = node
        
        # Point to the neighbors from the new node
        node.prev = prev_
        node.next = next_
        
        self._n_elems += 1

    def detach_node(self, node: Node) -> None:
        """Removes the node from the list"""
        
        # Update pointers to the node being removed
        prev_ = cast(Node, node.prev)
        prev_.next = node.next
        next_ = cast(Node, node.next)
        next_.prev = node.prev
        
        # Remove pointers from the node being removed
        node.next = None
        node.prev = None
        
        self._n_elems -= 1

    def _get(self):
        res = self.tail
        self.detach_node(res)
        return res
    
    def _size(self):
        return self._n_elems
    
    def to_list(self):
        return [node.key for node in self.iterate_nodes()]

    def iterate_nodes(self) -> Iterator[Node]:
        """Iterate over nodes in the list"""
        
        nodes = self.nil.forward()
        node = next(nodes)
        for node in nodes:
            yield node
        #
    
    def search(self, key: T) -> Node:
        """Return the first node containing the specified key.
        If not present, raises a ValueError"""
        for node in self.iterate_nodes():
            if node.key == key:
                return node
            #
        
        raise ValueError(f"{self.__class__.__name__} does not contain value {key}.")
    
    def insert(self, item: T):
        return self.put(item)
    
    def remove(self, item: T):
        node = self.search(item)
        self.detach_node(node)
    #
