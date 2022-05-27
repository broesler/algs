#!/usr/bin/env python3
# =============================================================================
#     File: buffer.py
#  Created: 2022-05-27 16:10
#   Author: Bernie Roesler
#
"""
Exercise 1.3.44 text editor buffer data type.
"""
# =============================================================================

from algs.basics import Collection, Stack

class Buffer(Collection):
    """Implements a buffer as would be used in a text editor.

    Attributes
    ----------
    cursor : char
        The character under the cursor.
    cursor_pos : int
        The position of the cursor from the left.
    size : int
        Number of characters in the buffer.
    """

    def __init__(self):
        self.sL = Stack()  # characters to the left of the cursor
        self.sR = Stack()  # characters to the right of the cursor

    @property
    def size(self):
        return self.sL.size + self.sR.size

    @property
    def cursor(self):
        return self.sR.peek()
    
    @property
    def cursor_pos(self):
        return self.sL.size

    def insert(self, c):
        """Insert `c` at the cursor position."""
        self.sL.push(c)

    def delete(self):
        """Delete the character under the cursor."""
        self.sL.pop()

    def left(self, k):
        """Move the cursor `k` positions to the left."""
        for _ in range(k):
            self.sR.push(self.sL.pop())

    def right(self, k):
        """Move the cursor `k` positions to the right."""
        for _ in range(k):
            self.sL.push(self.sR.pop())

    @property
    def _items(self):
        """Get a list of every in the buffer for iteration."""
        return self.sL._items + list(reversed(self.sR._items))
    
    def __str__(self):
        return ''.join(self._items)

    def print(self, with_cursor=True):
        """Print out text in buffer with cursor on another line."""
        print(self.__str__())
        print(self.sL.size*' ' + '^')


if __name__ == '__main__':
    b = Buffer()
    test = 'Stop. Collaborate. Ice is back with a new invention.'
    for c in test:
        b.insert(c)
    b.print()
    assert b.size == len(test)
    b.left(35)
    b.print()
    for c in ', and listen':
        b.insert(c)
    b.print()
    b.right(21)
    b.print()
    for c in 'brand ':
        b.insert(c)
    b.print()



# =============================================================================
# =============================================================================
