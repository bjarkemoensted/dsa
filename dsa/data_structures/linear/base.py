"""Implements a base class for simple linear data structures (stacks, queues)"""

from abc import ABC, abstractmethod
from typing import Iterator

DEFAULT_ARR_SIZE = 8


class Sentinel:
    """Reserved class for objects with special meanings.
    This is to have a class that's guaranteed to convey a special meaning, rather than e.g.
    using None, which may cause ambiguity if e.g. None can mean both 'missing value' or a value of None"""
    pass


class BaseContainer[T](ABC):
    """Base class for linear data structures. This is just to avoid boilerplate code for size logic etc"""
    
    def __init__(self, maxsize: int=-1):
        self.maxsize = maxsize
    
    def empty(self) -> bool:
        """Whether the data structure is currently empty"""
        res = self.size() == 0
        return res

    def __bool__(self) -> bool:
        return not self.empty()
    
    def full(self) -> bool:
        """Whether the data structure is currently full"""
        return self.size() == self.maxsize

    def _pre_get(self) -> None:
        if self.empty():
            raise RuntimeError(f"{self.__class__.__name__} is empty")
        
    def _pre_put(self, item: T) -> None:
        if self.full():
            raise RuntimeError(f"{self.__class__.__name__} is full, can't add item ({item})")

    @abstractmethod
    def size(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        raise NotImplementedError

    def to_list(self) -> list[T]:
        return [elem for elem in self]
