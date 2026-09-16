from __future__ import annotations

from collections.abc import Iterable, Iterator
from itertools import count
from typing import Literal, Self, cast, overload

from dsa.data_structures.linear.base import BaseContainer, Sentinel

NIL = Sentinel()


class Node[T]:
    """A node in a linked list.
    The value stored in the node is the key attribute.
    prev and next attributes point to the predessesor and successor nodes, respectively."""

    def __init__(self, key: T|Sentinel) -> None:
        """Initialize a node. If key is not provided, None is used initially.
        prev and next initially point to None - successor and predesssesor nodes
        must be set after initialization"""
        self._key: T|Sentinel = key
        self.prev: Node[T]|None = None
        self.next: Node[T]|None = None

    @property
    def key(self) -> T:
        if isinstance(self._key, Sentinel):
            raise TypeError("Attempted to access key on NIL node")
        return self._key

    @classmethod
    def make_nil(cls) -> Self:
        """Makes a sentinel node to represent NIL"""
        inst = cls(key=NIL)
        inst.prev = inst
        inst.next = inst
        return inst

    def _key_string(self) -> str:
        res = "NIL" if isinstance(self._key, Sentinel) else str(self._key)
        return res
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} <{self._key_string()}>"
    
    def __str__(self) -> str:
        return repr(self)

    def _iterate_direction(self, forward: bool=True) -> Iterator[Node[T]]:
        """Iterates over this node and all successors (if forward is True) or predessesors.
        Stops iteration if we run out of nodes, or if we arrive back at the starting node."""
        
        node = self
        while node:
            yield node
            next_node = node.next if forward else node.prev
            if not next_node or next_node is self:
                break
            node = next_node

    def forward(self) -> Iterator[Node]:
        """Iterates over this node and all successors"""
        yield from self._iterate_direction(forward=True)
    
    def backwards(self) -> Iterator[Node]:
        """Iterates over this node and all predecessor"""
        yield from self._iterate_direction(forward=False)


class LinkedList[T](BaseContainer[T]):
    """A linked list, where elements are stored with references to the next and previous elements.
    Uses a sentinel node to represent the beginning and end of the list.
    As the number of elements can't be efficiently computed without traversing the entire list,
    a counter is maintained when attaching new nodes or detaching current ones."""
    
    def __init__(self, values: Iterable[T]|None=None, maxsize: int = -1) -> None:
        super().__init__(maxsize)
        self.nil: Node[T] = Node.make_nil()
        self._n_elems: int = 0
        
        if values:
            self.extend(values)
    
    @property
    def head(self) -> Node[T]:
        """The head (first node) in the list"""
        return cast(Node[T], self.nil.next)
    
    @property
    def tail(self) -> Node[T]:
        """The tail (last node) in the list"""
        return cast(Node[T], self.nil.prev)

    def attach_node(self, item: T, insert_after: Node[T]|None=None) -> None:
        """Inserts a new node into the linked list.
        If insert_after is provided, the new node is inserted following the specified node.
        If not provided, the new node is inserted at the end of the list, and thus becomes the
        new tail."""

        node = Node(key=item)
        
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

    def detach_node(self, node: Node[T]) -> T:
        """Removes the node from the list"""

        self._pre_get()
        # Update pointers to the node being removed
        prev_ = cast(Node[T], node.prev)
        prev_.next = node.next
        next_ = cast(Node[T], node.next)
        next_.prev = node.prev
        
        # Remove pointers from the node being removed
        node.next = None
        node.prev = None
        
        self._n_elems -= 1

        res = node.key
        return res
    
    def size(self) -> int:
        return self._n_elems
    
    def iter_nodes(self, reverse: bool=False) -> Iterator[Node[T]]:
        """Iterate over nodes in the list"""
        
        nodes = self.nil.backwards() if reverse else self.nil.forward()
        _ = next(nodes)
        yield from nodes

    def __iter__(self, reverse: bool=False) -> Iterator[T]:
        elems = (node.key for node in self.iter_nodes(reverse))
        yield from elems
    
    def search(self, key: T) -> Node[T]:
        """Return the first node containing the specified key.
        If not present, raises a ValueError"""
        for node in self.iter_nodes():
            if node.key == key:
                return node
        
        raise ValueError(f"{self.__class__.__name__} does not contain value {key}.")
    
    def append(self, item: T) -> None:
        """Append to the tail (right) end of the list"""
        self.attach_node(item, insert_after=self.tail)
    
    def appendleft(self, item: T) -> None:
        """Append to the head (left) end of the list"""
        self.attach_node(item, insert_after=self.nil)

    def pop(self) -> T:
        """Pop from the head (right) end of the list"""
        return self.detach_node(node=self.tail)
    
    def popleft(self) -> T:
        """Pop from the tail (right) end of the list"""
        return self.detach_node(node=self.head)
    
    def extend(self, values: Iterable[T]) -> None:
        """Extend the tail (right) end of the list"""
        for value in values:
            self.append(value)
    
    def extendleft(self, values: Iterable[T]) -> None:
        """Extend the head (left) end of the list"""
        for value in values:
            self.appendleft(value)

    @overload
    def peek(self, i: int, return_node: Literal[True]) -> Node[T]: ...
    @overload
    def peek(self, i: int, return_node: Literal[False]=...) -> T: ...
    def peek(self, i: int, return_node: bool=False) -> Node[T]|T:
        # Define iterators for indices and nodes
        reverse = i < 0
        indices = count(start=-1, step=-1) if reverse else count(start=0, step=1)
        nodes = self.iter_nodes(reverse=reverse)

        for node in nodes:
            ind = next(indices)
            if ind == i:
                if return_node:
                    return node
                else:
                    return node.key
                #
            #
        raise IndexError(f"No node found at index {i}")
    
    def insert(self, item: T, index: int|None=None) -> None:
        """Insert an element into the list.
        If an index is provided, the element is inserted at that position if possible (if index
        is larger than the list, the element is inserted at the end)."""

        self._pre_put(item)
        target_node = self.tail if index is None else self.peek(index, return_node=True)

        return self.attach_node(item, insert_after=target_node)
    
    def remove(self, item: T) -> None:
        """Removes the first occurrence of a value fro mthe list"""
        node = self.search(item)
        self.detach_node(node)
