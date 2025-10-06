"""Implements a base class for simple linear data structures (stacks, queues)"""

from abc import ABC, abstractmethod
from typing import (
    Any,
    Generic,
    TypeVar
)


T = TypeVar('T')

DEFAULT_ARR_SIZE = 8


class BaseContainer(ABC, Generic[T]):
    """Base class for linear data structures. Has abstract methods for '_get' and '_put', which can be overridden
    to implement said operations. Aliases can then be defined for the terminology typically used for the specific data
    structure, i.e. push/pop for stacks, etc.
    The _get/_put methods are private to allow more generic public versions (get/put) to run common functionality
    before inserting/removing elements, such as checking if the data structures is full/empty.
    In addition, abstract methods _size and _to_list must also be defined for child classes"""
    
    def __init__(self, maxsize: int=-1):
        self.maxsize = maxsize
    
    def size(self):
        return self._size()
    
    def empty(self) -> bool:
        """Whether the data structure is currently empty"""
        res = self.size() == 0
        return res
    
    def full(self) -> bool:
        """Whether the data structure is currently full"""
        return self.size() == self.maxsize
    
    def get(self, **kwargs) -> T:
        if self.empty():
            raise RuntimeError(f"{self.__class__.__name__} is empty")
        return self._get(**kwargs)
    
    def put(self, item: T, **kwargs) -> None:
        if self.full():
            raise RuntimeError(f"{self.__class__.__name__} is full, can't add item ({item})")
        
        return self._put(item, **kwargs)
    
    @abstractmethod
    def _get(self) -> T:
        raise NotImplementedError
    
    @abstractmethod
    def _put(self, item: T) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def _size(self) -> int:
        raise NotImplementedError
    
    @abstractmethod
    def to_list(self) -> list[T]:
        raise NotImplementedError
    #
