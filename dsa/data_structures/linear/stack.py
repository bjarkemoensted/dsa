from typing import Iterator

from dsa.data_structures.linear.base import DEFAULT_ARR_SIZE, BaseContainer, Sentinel

# Represents an element which has been allocated but not yet set
NOT_SET = Sentinel()


class Stack[T](BaseContainer[T]):
    """Stack data structure. Implementation follows CLRS section 10.1.
    An invariant here is a .top pointer which points to the most recently inserted element.
    This implementation uses zero indexing, so the top pointer is initialized at -1 rather than 0."""

    arr: list[T | Sentinel]

    def __init__(self, maxsize: int=-1):
        super().__init__(maxsize=maxsize)
        initial_size = maxsize if maxsize != -1 else DEFAULT_ARR_SIZE
        self.arr = [NOT_SET for _ in range(initial_size)]
        self.top = -1  # pointer to the top of the stack

    def size(self) -> int:
        return self.top + 1

    def __iter__(self) -> Iterator[T]:
        if self.top < 0:
            return

        for elem in self.arr[:self.top+1]:
            if isinstance(elem, Sentinel):
                raise RuntimeError
            yield elem

    def push(self, item: T) -> None:
        """Pushes a single element onto the stack"""
        self._pre_put(item)

        # Grow the underlying array if we're out of space
        at_capacity = self.size() == len(self.arr)
        if at_capacity:
            self._grow_array()

        # increment pointer and add to the array
        self.top += 1
        self.arr[self.top] = item

    def pop(self) -> T:
        """Pops a single element from the stack"""
        self._pre_get()
        
        self.top -= 1
        res = self.arr[self.top + 1]

        if isinstance(res, Sentinel):
            raise RuntimeError("Popping an undefined element")
        return res

    def _grow_array(self) -> None:
        new_vals = (NOT_SET for _ in range(len(self.arr)))
        self.arr.extend(new_vals)
