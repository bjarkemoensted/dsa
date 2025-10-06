from __future__ import annotations
from typing import (
    cast,
    Generic,
    Iterable,
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
    
    def __init__(self, values: Iterable[T]|None=None, maxsize = -1) -> None:
        super().__init__(maxsize)
        self.nil: Node[T] = Node.make_nil()
        self._n_elems: int = 0
        
        if values:
            self.extend(values)
    
    def _put(self, item: T, insert_after: Node[T]|None=None):
        """Insert an element. If a node is specified, inserts after that node."""
        x = Node(key=item)
        self.attach_node(x, insert_after=insert_after)
    
    def _get(self, node: Node|None=None) -> T:
        """Retrieve the element stored at specified node."""
        node_ = node or self.tail
        self.detach_node(node_)
        res = node_.key
        return cast(T, res)
    
    @property
    def head(self) -> Node[T]:
        """The head (first node) in the list"""
        return cast(Node[T], self.nil.next)
    
    @property
    def tail(self) -> Node[T]:
        """The tail (last node) in the list"""
        return cast(Node[T], self.nil.prev)

    def attach_node(self, node: Node[T], insert_after: Node[T]|None=None) -> None:
        """Inserts a new node into the linked list.
        If insert_after is provided, the new node is inserted following the specified node.
        If not provided, the new node is inserted at the end of the list, and thus becomes the
        new tail."""
        
        # Determine the nodes which must come before and after the newly inserted node
        prev_ = insert_after or self.tail
        next_ = cast(Node[T], prev_.next)
        
        # Point to the new node from the neighbors in the list
        prev_.next = node
        next_.prev = node
        
        # Point to the neighbors from the new node
        node.prev = prev_
        node.next = next_
        
        self._n_elems += 1

    def detach_node(self, node: Node[T]) -> None:
        """Removes the node from the list"""
        
        # Update pointers to the node being removed
        prev_ = cast(Node[T], node.prev)
        prev_.next = node.next
        next_ = cast(Node[T], node.next)
        next_.prev = node.prev
        
        # Remove pointers from the node being removed
        node.next = None
        node.prev = None
        
        self._n_elems -= 1
    
    def _size(self):
        return self._n_elems
    
    def to_list(self):
        return [node.key for node in self.iterate_nodes()]

    def iterate_nodes(self) -> Iterator[Node[T]]:
        """Iterate over nodes in the list"""
        
        nodes = self.nil.forward()
        node = next(nodes)
        for node in nodes:
            yield node
        #
    
    def search(self, key: T) -> Node[T]:
        """Return the first node containing the specified key.
        If not present, raises a ValueError"""
        for node in self.iterate_nodes():
            if node.key == key:
                return node
            #
        
        raise ValueError(f"{self.__class__.__name__} does not contain value {key}.")
    
    def append(self, item: T) -> None:
        """Append to the tail (right) end of the list"""
        self.put(item, insert_after=self.tail)
    
    def appendleft(self, item: T) -> None:
        """Append to the head (left) end of the list"""
        self.put(item, insert_after=self.nil)
    
    def pop(self) -> T:
        """Pop from the head (right) end of the list"""
        return self.get(node=self.tail)
    
    def popleft(self) -> T:
        """Pop from the tail (right) end of the list"""
        return self.get(node=self.head)
    
    def extend(self, values: Iterable[T]) -> None:
        """Extend the tail (right) end of the list"""
        for value in values:
            self.append(value)
        #
    
    def extendleft(self, values: Iterable[T]) -> None:
        """Extend the head (left) end of the list"""
        for value in values:
            self.appendleft(value)
    
    def insert(self, item: T, index: int=0):
        """Insert an element into the list.
        If an index is provided, the element is inserted at that position if possible (if index
        is larger than the list, the element is inserted at the end)."""

        for i, node in enumerate(self.iterate_nodes()):
            if i == index:
                return self.put(item, insert_after=node)
        return self.put(item)
    
    def remove(self, item: T):
        """Removes the first occurrence of a value fro mthe list"""
        node = self.search(item)
        self.detach_node(node)
    #
