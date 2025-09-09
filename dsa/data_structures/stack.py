from typing import Generic, TypeVar

T = TypeVar('T')


class Stack(Generic[T]):
    """Stack data structure. Implementation follows CLRS section 10.1."""
    
    arr: list[T]
    
    def __init__(self, maxsize: int=-1):
        self.arr = []
        self.top = 0
        self.maxsize = maxsize
    
    def empty(self) -> bool:
        """Checks whether the stack is empty"""
        
        assert self.top >= 0
        res = self.top == 0
        return res

    def full(self) -> bool:
        """Checks whether the stack is full"""
        if self.maxsize == -1:
            return False
        else:
            return self.top >= self.maxsize

    def pop(self) -> T:
        """Pops a single element from the stack"""
        if self.empty():
            raise RuntimeError("Can't pop from empty list")
        
        self.top -= 1
        res = self.arr[self.top]
        return res
    
    def push(self, elem: T) -> None:
        """Pushes a single element onto the stack"""
        if self.full():
            raise RuntimeError(f"Can't push to full stack")
        
        self.top += 1
        needs_extension = self.top == len(self.arr) + 1
        
        if needs_extension:
            self.arr.append(elem)
        else:
            self.arr[self.top] = elem
    #
