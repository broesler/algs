#!/home/broesler/anaconda3/envs/expo/bin/python3
#==============================================================================
#     File: stack.py
#  Created: 2019-02-08 17:23
#   Author: Bernie Roesler
#
"""
  Description: Implement a basic Stack data structure
"""
#==============================================================================

class Stack():
    """Implement a Stack data structure.

    Parameters
    ----------
    items : iterable 
        List of items to push onto the stack, in LIFO order.

    Attributes
    -------
    size : int
        Number of items on the stack.
    is_empty : bool
        True if `size == 0`.
    """
    def __init__(self, items=list()):
        # _items[0] is "top" of stack
        self._items = list(items)[::-1]

    @property
    def size(self):
        return len(self._items)

    @property
    def is_empty(self):
        return (self.size == 0)

    def peek(self):
        """Look at top of stack without popping.""" 
        return self._items[0]

    def pop(self):
        """Remove and return item from top of stack."""
        return self._items.pop(0)

    def push(self, item):
        """Add item to top of stack."""
        self._items.insert(0, item)

    def __iter__(self):
        yield from self._items

    def __bool__(self):
        return bool(self.size)

    def __str__(self):
        # print from top of stack
        return str(self._items)

if __name__ == '__main__':
    s = Stack()
    for i in range(5):
        s.push(i)
    assert s.size == 5
    assert not s.is_empty
    assert 4 == s.peek()
    assert 4 == s.pop()
    assert str(s) == '[3, 2, 1, 0]'
    # Test iteration
    for i, item in zip([3, 2, 1, 0], s):
        assert i == item

#==============================================================================
#==============================================================================
