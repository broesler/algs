#!/usr/bin/env python3
# =============================================================================
#     File: special.py
#  Created: 2022-06-07 17:04
#   Author: Bernie Roesler
#
"""
Menagerie of classes that use symbol tables, but don't quite fit in elsewhere.
"""
# =============================================================================

from collections import deque

from algs.basics import Queue
from algs.search import HashSet, ST, HashST


# Exercise 3.5.27
class List():
    """A data type similar to a deque, but using symbol tables to support
    efficient operations."""

    def __init__(self, items=None):
        items = items or []
        self._items = deque()
        self._locs = HashST()  # store index locations by key
        self._idxs = ST()      # store keys by index location
        for item in items:
            self.add_back(item)

    def size(self):
        pass

    def is_empty(self):
        return self.size() == 0

    def add_front(self, item):
        """Add an item to the front of the list."""
        pass

    def add_back(self, item):
        """Add an item to the back of the list."""
        pass

    def delete_front(self):
        """Delete an item from the front."""
        pass

    def delete_back(self):
        """Delete an item from the back."""
        pass

    def remove(self, item):
        """Remove `item` from the list."""
        pass

    def add(self, i, item):
        """Add `item` as the `i`th element in the list."""
        pass

    def delete(self, i=0):
        """Remove the `i`th item from the list."""
        pass

    def __contains__(self, item):
        """Return True if `item` is in the list."""
        pass

    def __iter__(self):
        """Return an iterator over the List."""
        pass


# Exercise 3.5.28
class Uniqueue(Queue):
    """A queue, except an element may only be inserted once."""

    def __init__(self, items=None):
        items = items or []
        self._st = HashSet()
        super().__init__()
        for item in items:
            self.enqueue(item)

    def enqueue(self, item):
        if item not in self._st:
            self._st.add(item)
            super().enqueue(item)


if __name__ == '__main__':
    keys = list('SEARCHEXAMPLE')
    q = Uniqueue(keys)
    print(q)

# =============================================================================
# =============================================================================
