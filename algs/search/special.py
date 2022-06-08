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
from algs.search import Set, HashSet, ST, HashST


# Exercise 3.5.27
class List():
    """A data type similar to a deque, but using symbol tables to support
    efficient operations. Dupilcate elements are allowed."""

    # TODO how to adjust indices of items added/removed from the middle??
    def __init__(self, items=None):
        items = items or []
        self._F = 0  # index of front of List
        self._N = 0  # index of back of List
        self._locs = HashST()  # store index locations by key, _locs[k] = i
        self._keys = ST()      # store keys by index location, _keys[i] = k
        for item in items:
            self.add_back(item)

    def size(self):
        return self._N - self._F

    def is_empty(self):
        return self.size() == 0

    # TODO allow `i` to be a slice
    def __getitem__(self, i):
        """Return the item at index `i`."""
        if i < 0:
            i += self.size()
        if i < 0 or i >= self.size():
            raise IndexError(i)
        return self._keys[self._F + i]

    def index(self, k):
        """Return the first index of the key `k`."""
        return self._locs[k].min()

    def add_front(self, item):
        """Add an item to the front of the list."""
        self._F -= 1
        if item not in self._locs:
            self._locs[item] = Set()
        self._locs[item].add(self._F)
        self._keys[self._F] = item

    def add_back(self, item):
        """Add an item to the back of the list."""
        if item not in self._locs:
            self._locs[item] = Set()  # unique, sorted list of indices
        self._locs[item].add(self._N)
        self._keys[self._N] = item
        self._N += 1

    def delete_front(self):
        """Delete an item from the front."""
        k = self._keys[self._F]
        self._locs[k].delete_min()
        if self._locs[k].is_empty:
            del self._locs[k]
        del self._keys[self._F]
        self._F += 1

    def delete_back(self):
        """Delete an item from the back."""
        self._N -= 1
        k = self._keys[self._N]
        self._locs[k].delete_max()
        if self._locs[k].is_empty:
            del self._locs[k]
        del self._keys[self._N]

    def remove(self, item):
        """Remove `item` from the list."""
        pass

    def add(self, i, item):
        """Add `item` as the `i`th element in the list."""
        pass

    def __delitem__(self, i):
        pass

    def __contains__(self, item):
        return item in self._locs

    def delete(self, i):
        """Remove the `i`th item from the list."""
        self.__delitem__(i)

    def contains(self, k):
        """Return True if `item` is in the list."""
        return self.__contains__(k)

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __iter__(self):
        """Return an iterator over the List."""
        yield from self._keys.values()


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

    a = List(keys)
    print(a)
    assert a.size() == len(keys)
    for i, c in enumerate(keys):
        assert a[i] == c
        # assert a.index(c) == i
    a.delete_back()
    assert a.size() == len(keys)-1
    print(a)
    a.add_front('X')
    assert a.size() == len(keys)
    print(a)
    a.delete_front()
    assert a.size() == len(keys)-1
    print(a)

# =============================================================================
# =============================================================================
