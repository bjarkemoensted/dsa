from typing import cast

from dsa.data_structures.linear.queue import DEFAULT_ARR_SIZE, BaseContainer


class Stack[T](BaseContainer):
    """Stack data structure. Implementation follows CLRS section 10.1.
    An invariant here is a .top pointer which points to the most recently inserted element.
    This implementation uses zero indexing, so the top pointer is initialized at -1 rather than 0."""

    arr: list[T | None]

    def __init__(self, maxsize: int=-1):
        super().__init__(maxsize=maxsize)
        initial_size = maxsize if maxsize != -1 else DEFAULT_ARR_SIZE
        self.arr = [None for _ in range(initial_size)]
        self.top = -1  # pointer to the top of the stack

    def _size(self) -> int:
        return self.top + 1

    def _get(self) -> T:
        """Pops a single element from the stack"""
        self.top -= 1
        res = self.arr[self.top + 1]
        return cast(T, res)

    def _put(self, item: T) -> None:
        """Pushes a single element onto the stack"""
        # Grow the underlying array if we're out of space
        at_capacity = self.size() == len(self.arr)
        if at_capacity:
            self._grow_array()

        # increment pointer and add to the array
        self.top += 1
        self.arr[self.top] = item

    def push(self, item: T) -> None:
        self.put(item)

    def pop(self) -> T:
        return self.get()

    def _grow_array(self) -> None:
        new_vals = (None for _ in range(len(self.arr)))
        self.arr.extend(new_vals)

    def to_list(self) -> list[T]:
        res = [self.arr[i] for i in range(self.top + 1)]
        return cast(list[T], res)
