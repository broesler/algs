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

from algs.basics import Collection, Queue, RandomQueue, DoubleList
from algs.search import Set, HashSet, ST, HashST


# Exercise 3.5.26
class LRUCache(Collection):
    """An implementation of a cache using the least-recently-used (LRU)
    replacement policy."""

    def __init__(self, items=None):
        self._items = DoubleList()
        self._st = HashST()  # store locations in the list by key
        items = items or []
        for item in items:
            self.access(item)

    @property
    def _N(self):
        return self._items.size

    def access(self, item):
        """Add `item` to the front of the list if it does not already exist."""
        if item not in self._st:
            self._items.add_front(item)
            self._st[item] = self._items._first
        else:
            # Move the item to the front of the list
            x = self._st[item]
            self._items.move_to_front(x)

    def remove(self):
        """Remove the least-recently used item from the back of the list."""
        x = self._items.remove_back()
        del self._st[x.data]
        return x.data


# Exercise 3.5.27
class List(Collection):
    """A data type similar to a deque, but using symbol tables to support
    efficient operations. Dupilcate elements are allowed."""
    _LO = 0.0
    _HI = 1.0
    _BASE = 0.1  # bias towards front since constructor adds to back

    def __init__(self, items=None):
        self._N = 0
        self._locs = HashST()  # store index locations by key, _locs[k] = i
        self._keys = ST()      # store keys by index location, _keys[i] = k
        items = items or []
        for item in items:
            self.add_back(item)

    @property
    def size(self):
        return self._N

    @property
    def _items(self):
        """Return an iterable over the List."""
        return self._keys.values()

    def _validate_index(self, i):
        """Return a use-able index, or raise an IndexError."""
        if i < 0:
            i += self.size
        if i < 0 or i >= self.size:
            raise IndexError(i)
        return i

    # TODO allow `i` to be a slice
    def __getitem__(self, i):
        """Return the item at index `i`."""
        i = self._validate_index(i)
        return self._keys[self._keys.select(i)]

    def index(self, k):
        """Return the first index of the key `k`."""
        self._empty_check()
        if k not in self._locs:
            raise KeyError(k)
        return self._keys.rank(self._locs[k].min())

    def add_front(self, item):
        """Add an item to the front of the list."""
        f = self._BASE if self.is_empty else (self._LO + self._keys.min()) / 2
        if item not in self._locs:
            self._locs[item] = Set()
        self._locs[item].add(f)
        self._keys[f] = item
        self._N += 1

    def add_back(self, item):
        """Add an item to the back of the list."""
        f = self._BASE if self.is_empty else (self._keys.max() + self._HI) / 2
        if item not in self._locs:
            self._locs[item] = Set()  # unique, sorted list of indices
        self._locs[item].add(f)
        self._keys[f] = item
        self._N += 1

    def delete_front(self):
        """Delete an item from the front."""
        self._empty_check()
        k = self._keys[self._keys.min()]
        self._locs[k].delete_min()
        if self._locs[k].is_empty:
            self._locs.delete(k)
        self._keys.delete_min()
        self._N -= 1

    def delete_back(self):
        """Delete an item from the back."""
        self._empty_check()
        k = self._keys[self._keys.max()]
        self._locs[k].delete_max()
        if self._locs[k].is_empty:
            self._locs.delete(k)
        self._keys.delete_max()
        self._N -= 1

    def remove(self, item):
        """Remove the lowest-index instance of `item` from the list."""
        if item not in self._locs:
            raise KeyError(item)
        f = self._locs[item].min()
        self._keys.delete(f)
        self._locs[item].delete_min()
        self._N -= 1

    def add(self, i, item):
        """Add `item` as the `i`th element in the list."""
        i = self._validate_index(i)
        if self.is_empty:
            f = self._BASE
        else:
            f = (self._keys.select(i) + self._keys.select(i-1)) / 2
        if item not in self._locs:
            self._locs[item] = Set()
        self._locs[item].add(f)
        self._keys[f] = item
        self._N += 1

    def __delitem__(self, i):
        """Remove the `i`th item from the list."""
        i = self._validate_index(i)
        f = self._keys.select(i)
        k = self._keys[f]
        self._locs[k].delete(f)
        if self._locs[k].is_empty:
            self._locs.delete(k)
        self._keys.delete(f)
        self._N -= 1

    def __contains__(self, item):
        """Return True if `item` is in the list."""
        return item in self._locs

    def delete(self, i):
        """Remove the `i`th item from the list."""
        self.__delitem__(i)

    def contains(self, k):
        """Return True if `item` is in the list."""
        return self.__contains__(k)


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


# Exercise 3.5.29
class RandomST(HashST):
    """Implements a symbol table with random access."""

    def __init__(self, items=None, *args, **kwargs):
        self._q = RandomQueue()
        super().__init__(items, *args, **kwargs)

    def __setitem__(self, k, v):
        self._q.enqueue(k)
        super().__setitem__(k, v)

    # Could do:
    # self._q._items.remove(k)
    # super().__delitem__(k)
    # but remove is O(N).
    def __delitem__(self, k):
        raise NotImplementedError('Deletion by key not supported! Use pop().')

    def pop(self):
        """Remove and return a random key."""
        k = self._q.dequeue()
        super().__delitem__(k)
        return k


if __name__ == '__main__':
    keys = list('SEARCHEXAMPLE')

    print('----- LRUCache -----')
    c = LRUCache(keys)
    print(c)
    assert list(c._items) == list('ELPMAXHCRS')
    assert len(c) == len(set(keys))
    assert c.remove() == 'S'
    assert len(c) == len(set(keys))-1

    print('----- List -----')
    a = List(keys)
    print(a)
    assert a.size == len(keys)
    for i, c in enumerate(keys):
        assert a[i] == c
        # assert a.index(c) == i
    a.delete_back()
    assert a.size == len(keys)-1
    print(a)
    a.add_front('X')
    assert a.size == len(keys)
    print(a)
    a.delete_front()
    assert a.size == len(keys)-1
    print(a)
    a.add_back('E')
    a.add(6, 'Z')
    print(a)
    assert a.size == len(keys)+1
    a.remove('A')
    print(a)
    assert a.size == len(keys)
    del a[5]
    print(a)
    assert a.size == len(keys)-1

    print('----- Uniqueue -----')
    q = Uniqueue(keys)
    print(q)
    assert q.dequeue() == 'S'
    print(q)

    print('----- RandomST -----')
    items = [(k, i) for i, k in enumerate(keys)]
    st = RandomST(items)
    assert st['A'] == 8
    print(st)
    assert st.pop() in keys

# =============================================================================
# =============================================================================
