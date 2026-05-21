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

import numpy as np

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
    efficient operations. Duplicate elements are allowed."""
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


# Web Exercise 9
class IndirectPQ(Collection):
    """Implements an indirect priority queue. This class is similar to
    a priority queue, but allows deletion of any element by name"""

    class _Item:
        """An internal class to hold a key and its priority."""
        def __init__(self, key, priority=0):
            self.key = key
            self.priority = priority

        # Could pass key=lambda x x.priority to PriorityQueue() instead
        # Define the comparison functions so that the items are ordered
        # properly in the priority queue.
        def __lt__(self, other):
            return self.priority < other.priority

        def __gt__(self, other):
            return self.priority > other.priority

        def __eq__(self, other):
            return self.key == other.key and self.priority == other.priority

        def __str__(self):
            return f"({repr(self.key)}: {repr(self.priority)})"

        def __repr__(self):
            return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __init__(self, items=None):
        # NOTE *delete* not implemented in PriorityQueue. We do not have an
        # efficient way of computing the _index_ of a given key for an array
        # binary heap structure.
        # self._pq = PriorityQueue(kind='max')
        self._pq = Set()  # use ordered set
        self._st = HashST()
        items = items or []
        for k, p in items:
            self.put(k, p)

    @property
    def _items(self):
        return [x.key for x in self._pq]

    def __setitem__(self, k, p=0):
        """Add an item `k` to the queue with priority `p`."""
        self.__delitem__(k)
        x = self._Item(k, p)
        self._st[k] = x
        self._pq.add(x)

    def __delitem__(self, k):
        """Remove key `k` from the queue."""
        if k in self._st:
            x = self._st[k]
            self._pq.delete(x)
            self._st.delete(k)

    def __getitem__(self, k):
        """Return the priority of a key."""
        return self._st[k].priority

    def __contains__(self, k):
        """Return True if `k` is in the queue."""
        return k in self._st

    def min(self):
        """Return the minimum priority."""
        return self._pq.min().priority

    def max(self):
        """Return the maximum priority."""
        return self._pq.max().priority

    def delete_min(self):
        """Delete and return the key with the minimum priority."""
        k = self._pq.min().key
        self._pq.delete_min()
        self._st.delete(k)
        return k

    def delete_max(self):
        """Delete and return the key with the maximum priority."""
        k = self._pq.max().key
        self._pq.delete_max()
        self._st.delete(k)
        return k

    # aliases
    def put(self, k, p):
        return self.__setitem__(k, p)

    def get(self, k):
        return self.__getitem__(k)


# Web Exercise 9
class BloomFilter():
    r"""Implements a hash table with only `add` and `exists` operations.
    Determines if an element is definitively *not* in the set, or *may* be in
    the set with probability << 1.

    Attributes
    ----------
    size : int
        The number of elements in the set.
    is_empty : bool
        True if `size == 0`.
    M : int
        The number of bits in the hash table.
    nbits : int
        The number of bits set to 1.
    prob : float
        The probability of a false positive `exists` operation.

    Notes
    -----
    The optimal number of hash functions is :math:`k = ln(2) * M/N`.
    The number of bits per element *b = M/N* is:

    .. math::
        b = \frac{\log\frac{1}{p}}{\log^2 2}

    where *p* is the false positive probability.

    The values of this expression are:
        p      b
        0.001  14.38
        0.003  12.32
        0.007  10.27
        0.019   8.22
        0.052   6.16
        0.139   4.11
        0.373   2.05
        1.000   0.00
    so choosing *b = 8* gives ~ 2% false positive rate.
    """

    # TODO allow client to set the false positive rate, then choose `b` and `M`
    # based on (expected) N = len(keys)
    def __init__(self, keys=None, p=0.02):
        keys = keys or []
        if len(keys) > 0:
            M = int(-len(keys) * np.log2(p) / np.log(2))  # optimal M given `p`
        self.N = 0
        self.M = M
        self.k = int(-np.log2(p))  # optimal `k` given M and N
        self._bits = np.zeros(self.M, dtype=bool)
        try:
            for key in keys:
                self.add(key)
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             'expects an iterable input.')

    def size(self):
        return self.N

    @property
    def is_empty(self):
        return self.size() == 0

    @property
    def nbits(self):
        """Return the number of bits set to 1."""
        return self._bits.sum()

    @property
    def prob(self):
        return (1 - np.exp(-self.k*self.N/self.M))**self.k

    def _hash0(self, k):
        """Take the upper 32 bits of a 64-bit hash function."""
        return hash(k) >> 32

    def _hash1(self, k):
        """Take the lower 32 bits of a 64-bit hash function."""
        return hash(k) & ((1 << 32) - 1)

    def _hash(self, k, i=0):
        """Combine two hash functions to get the `i`th hash function using the
        Kirsch-Mitzenmacher optimization [0].

        .. [0]:: <https://www.eecs.harvard.edu/~michaelm/postscripts/tr-02-05.pdf>
        """
        return (self._hash0(k) + i*self._hash1(k)) % self.M

    def _hashes(self, key):
        """Return all `k` hashes for `key`."""
        h0 = self._hash0(key)
        h1 = self._hash1(key)
        return [(h0 + i*h1) % self.M for i in range(self.k)]

    def add(self, key):
        """Add an element to the set by setting corresponding bits to True."""
        if key not in self:
            self._bits[self._hashes(key)] = True
            self.N += 1

    def __contains__(self, key):
        """Return False if an element is not in the set. If True, the element
        *may* not be in the set with small probability."""
        return all(self._bits[self._hashes(key)])


# TODO move to unit tests
if __name__ == '__main__':
    import string
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

    print('----- IndirectPQ -----')
    items = [(k, i) for i, k in enumerate(keys)]
    st = IndirectPQ(items)
    print(st)
    print(st.delete_min())
    print(st)
    print(st.delete_max())
    print(st)

    print('----- BloomFilter -----')
    # TODO test probabilistically with large number of integers to show that
    # *p* percent of time, `k in bf` returns True when `k` is not, in fact, in
    # the table.
    bf = BloomFilter(keys)
    assert bf.size() == 10
    for k in keys:
        assert k in bf
    for k in string.ascii_uppercase:
        print(f"{k}: {k in bf}")
    print(10*'-')
    print(f"{bf.N = }")
    print(f"{bf.M = }")
    print(f"{bf.k = }")
    print(f"{bf.N/bf.M = :.4g}")
    print(f"{bf.nbits = }")
    print(f"{bf.prob = :.4g}")

# =============================================================================
# =============================================================================
