#!/usr/bin/env python3
# =============================================================================
#     File: hash.py
#  Created: 2022-04-21 17:48
#   Author: Bernie Roesler
#
"""
  Description: Hash Tables.
"""
# =============================================================================

import math

from algs.search.table import SequentialSearchST as _SequentialSearchST

__all__ = ['SeparateChainingHashST', 'SeparateChainingLiteHashST',
           'LinearProbingHashST']

# TODO constructor `from_tuples` that takes items = [('a', 0), ('b', 2), ...]
# constructor 'from_keys` that takes keys = ['a', 'b', ...] and value = None.

# Table of primes greater than the nearest power of 2
_PRIMES = dict({
    5: 31,
    6: 61,
    7: 127,
    8: 251,
    9: 509,
    10: 1021,
    11: 2039,
    12: 4093,
    13: 8191,
    14: 16381,
    15: 32749,
    16: 65521,
    17: 131071,
    18: 262139,
    19: 524287,
    20: 1048573,
    21: 2097143,
    22: 4194301,
    23: 8388593,
    24: 16777213,
    25: 33554393,
    26: 67108859,
    27: 134217689,
    28: 268435399,
    29: 536870909,
    30: 1073741789,
    31: 2147483647
})


class SeparateChainingHashST():
    """Implements a hash table with separate chaining.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) pairs to be put into the table.
    M : int
        Number of slots in the hash table.

    Attributes
    ----------
    size : int
        Number of key-value pairs.
    is_empty : bool
        True if `size == 0`.

    Raises
    ------
    KeyError
        If `k` is not in the table.
    """
    INIT_CAPACITY = 4  # minimum number of hash slots

    def __init__(self, items=None, M=None, max_probes=10, cache=False):
        self.N = 0
        self.M = M or self.INIT_CAPACITY
        self._MAX_PROBES = max_probes  # maximum average list size
        self._lgM = int(math.log2(self.M))
        # Initialize the symbol table
        self._st = [_SequentialSearchST() for _ in range(self.M)]
        items = items or []  # must be iterable
        try:
            for k, v in items:
                self.__setitem__(k, v)
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             'expects an iterable mapping input.')

    @property
    def is_empty(self):
        return self.size == 0

    @property
    def size(self):
        return self.N

    def _validate_size(self):
        assert self.size == sum([t.size for t in self._st])

    def _hash(self, k):
        """Modular hashing using Python's built-in `hash` function."""
        # NOTE `hash` is "salted" each time python is run for security reasons,
        # so results are non-deterministic. Manual override or set seed?
        # return hash(k) % self.M
        # Exercise 3.4.18: ensure items evenly distributed when M is power of 2
        t = hash(k)
        if self._lgM < 26:
            t = t % _PRIMES[self._lgM + 5]
        return t % self.M

    def _resize(self, M):
        """Resize the array of hash slots."""
        # Create a new table and hash the existing keys into it
        t = SeparateChainingHashST(self.items(), M=M)
        # Use the new table in *self*
        self._st = t._st
        self.M = t.M
        self._lgM = int(math.log2(self.M))  # see Exercise 3.4.18

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`."""
        # Double table size if average list length >= MAX_PROBES (e.g. 10)
        if self.N >= self._MAX_PROBES*self.M:
            self._resize(2*self.M)
        i = self._hash(k)
        if k not in self._st[i]:
            self.N += 1
        self._st[i][k] = v

    def __getitem__(self, k):
        """Return the value associated with the given key `k`."""
        return self._st[self._hash(k)][k]

    # Exercise 3.4.9, eager delete
    def __delitem__(self, k):
        """Delete the item associated with `k`."""
        i = self._hash(k)
        if k in self._st[i]:
            self.N -= 1
        del self._st[i][k]
        # Halve table size if average list length <= 2
        if self.M > self.INIT_CAPACITY and self.N <= 2*self.M:
            self._resize(self.M // 2)

    def __len__(self):
        return self.size

    def __contains__(self, k):
        """Return True if `k` is present in the table, False otherwise."""
        try:
            self.__getitem__(k)
            return True
        except KeyError:
            return False

    def __eq__(self, other):
        return sorted(self.items()) == sorted(other.items())

    def __str__(self):
        out = ''
        for i, t in enumerate(self._st):
            out += f"[{i}]: {repr(t)}\n"
        return out

    def __repr__(self):
        return f"<{self.__class__.__name__}:\n{self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Iterator functions
    # -------------------------------------------------------------------------
    # Exercise 3.4.19
    _docstring = """Return an in-order iterator over the {rtype}`.

    Returns
    -------
    q : iterator
        iterator over the {rtype}.
    """

    def keys(self):
        return self._make_iterator(rtype='keys')(self)

    def values(self):
        return self._make_iterator(rtype='values')(self)

    def items(self):
        return self._make_iterator(rtype='items')(self)

    keys.__doc__   = _docstring.format(rtype='keys')
    values.__doc__ = _docstring.format(rtype='values')
    items.__doc__  = _docstring.format(rtype='items')

    def __iter__(self):
        """Return an iterator of all of the keys in the table."""
        yield from self.keys()

    def _make_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        def iterator(self, lo=None, hi=None):
            """Iterate over each symbol table."""
            q = list()
            for t in self._st:
                q.extend(t.keys() if rtype == 'keys' else
                         (t.values() if rtype == 'values' else t.items()))
            return q
        return iterator


# Exercise 3.4.2
class SeparateChainingLiteHashST():
    """Implements a hash table with separate chaining, but uses a nested linked
    list insteady of `SequentialSearchST` dependency.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) pairs to be put into the table.
    M : int
        Number of slots in the hash table.

    Attributes
    ----------
    size : int
        Number of key-value pairs.
    is_empty : bool
        True if `size == 0`.

    Raises
    ------
    KeyError
        If `k` is not in the table.
    """
    INIT_CAPACITY = 4  # minimum number of hash slots

    # Private class of key/value pairs
    class _Node():
        """Internal item object to hold key and value."""
        def __init__(self, key, value, next=None, N_before=0):
            self.key = key
            self.val = value
            self.N_before = N_before  # entries in table when Node created
            self.next = next

        def __str__(self):
            return f"({repr(self.key)}: {repr(self.val)})"

        def __repr__(self):
            return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __init__(self, items=None, M=None, max_probes=10, cache=False):
        self.N = 0
        self.M = M or self.INIT_CAPACITY
        self._MAX_PROBES = max_probes  # maximum average list size
        self._lgM = int(math.log2(self.M))
        # Initialize the symbol table
        self._st = self.M*[None]   # Create M linked lists
        items = items or []  # must be iterable
        try:
            for k, v in items:
                self.__setitem__(k, v)
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             'expects an iterable mapping input.')

    @property
    def is_empty(self):
        return self.N == 0

    @property
    def size(self):
        return self.N

    def _hash(self, k):
        """Modular hashing using Python's built-in `hash` function."""
        # return hash(k) % self.M
        # Exercise 3.4.18: ensure items evenly distributed when M is power of 2
        t = hash(k)
        if self._lgM < 26:
            t = t % _PRIMES[self._lgM + 5]
        return t % self.M

    def _resize(self, M):
        """Resize the array of hash slots."""
        # Create a new table and hash the existing keys into it
        t = SeparateChainingLiteHashST(self.items(), M=M)
        # Use the new table in *self*
        self._st = t._st
        self.M = t.M
        self._lgM = int(math.log2(self.M))  # see Exercise 3.4.18

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`."""
        # Double table size if average list length >= 10
        if self.N >= self._MAX_PROBES*self.M:
            self._resize(2*self.M)

        # Hash into table
        i = self._hash(k)
        x = self._st[i]

        if x is None:
            # Create new linked list at hash table location
            self._st[i] = self._Node(k, v, N_before=self.N)
            self.N += 1
            return

        # There is a hash collision. Search for key.
        while x:
            if k == x.key:
                x.val = v
                return
            else:
                x = x.next
        else:
            # Insert new node at beginning of list
            self._st[i] = self._Node(k, v, self._st[i], N_before=self.N)
            self.N += 1

    def __getitem__(self, k):
        """Return the value associated with the given key `k`."""
        x = self._st[self._hash(k)]
        while x:
            if k == x.key:
                return x.val
            else:
                x = x.next
        else:
            raise KeyError(k)

    def __delitem__(self, k):
        """Delete the item associated with `k`."""
        i = self._hash(k)
        x = self._st[i]
        if x is None:
            raise KeyError(k)

        # Check the first node
        if k == x.key:
            self._st[i] = x.next
            self.N -= 1
            return

        while x.next:
            if k == x.next.key:
                x.next = x.next.next  # unlink the node
                self.N -= 1
                return
            else:
                x = x.next
        else:
            raise KeyError(k)

        # Halve table size if average list length <= 2
        if self.M > self.INIT_CAPACITY and self.N <= 2*self.M:
            self._resize(self.M // 2)

    # Exercise 3.4.3
    def delete_later_than(self, k):
        """Delete all entries in the table that were inserted after `k`."""
        for i in range(self.M):
            if self._st[i] is None:
                continue
            # Larger numbers will always be at the front of the table given our
            # insert-at-front algorithm. Keep deleting from front.
            x = self._st[i]
            while x:
                if x.N_before > k:
                    self._st[i] = x.next
                    self.N -= 1
                x = x.next

    def __len__(self):
        return self.size

    def __contains__(self, k):
        """Return True if `k` is present in the table, False otherwise."""
        try:
            self.__getitem__(k)
            return True
        except KeyError:
            return False

    def __eq__(self, other):
        return sorted(self.items()) == sorted(other.items())

    def __str__(self):
        out = ''
        for i, t in enumerate(self._st):
            x = t
            out += f"[{i}]: ["
            while x:
                out += str(x)
                if x.next:
                    out += ", "
                x = x.next
            out += "]\n"
        return out

    def __repr__(self):
        return f"<{self.__class__.__name__}:\n{self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Iterator functions
    # -------------------------------------------------------------------------
    # Exercise 3.4.19
    _docstring = """Return an in-order iterator over the {rtype}`.

    Returns
    -------
    q : iterator
        iterator over the {rtype}.
    """

    def keys(self):
        return self._make_iterator(rtype='keys')(self)

    def values(self):
        return self._make_iterator(rtype='values')(self)

    def items(self):
        return self._make_iterator(rtype='items')(self)

    def _nodes(self):
        return self._make_iterator(rtype='nodes')(self)

    keys.__doc__   = _docstring.format(rtype='keys')
    values.__doc__ = _docstring.format(rtype='values')
    items.__doc__  = _docstring.format(rtype='items')

    def __iter__(self):
        """Return an iterator of all of the keys in the table."""
        yield from self.keys()

    def _make_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        def iterator(self, lo=None, hi=None):
            """Iterate over each symbol table."""
            q = list()
            for t in self._st:
                x = t
                while x:
                    q.append(x.key if rtype == 'keys' else
                             (x.val if rtype == 'values' else 
                             (x.key, x.val) if rtype == 'items' else x))
                    x = x.next
            return q
        return iterator


class LinearProbingHashST():
    """Implements a hash table using arrays with linear probing.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) pairs to be put into the table.
    M : int
        Number of slots in the hash table.

    Attributes
    ----------
    size : int
        Number of key-value pairs.
    is_empty : bool
        True if `size == 0`.

    Raises
    ------
    KeyError
        If `k` is not in the table.
    """
    def __init__(self, items=None, M=16, cache=False):
        self.M = M
        self.N = 0
        items = items or []  # must be iterable
        # Initialize the symbol table
        self._keys = M*[None]
        self._vals = M*[None]
        try:
            for k, v in items:
                self.__setitem__(k, v)
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             'expects an iterable mapping input.')

    @property
    def is_empty(self):
        return self.size == 0

    @property
    def size(self):
        return self.N

    def _hash(self, k):
        return hash(k) % self.M

    def _resize(self, M):
        """Resize the internal keys and values arrays."""
        # Create a new table and hash the existing keys into it
        t = LinearProbingHashST(M=M)
        for i in range(self.M):
            if self._keys[i] is not None:
                t[self._keys[i]] = self._vals[i]
        # Use those new arrays in *self*
        self._keys = t._keys
        self._vals = t._vals
        self.M = t.M

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`."""
        if self.N >= self.M // 2:
            self._resize(2*self.M)
        i = self._hash(k)
        while self._keys[i] is not None:
            if k == self._keys[i]:
                self._vals[i] = v
                return
            else:
                i = (i + 1) % self.M
        else:
            self._keys[i] = k
            self._vals[i] = v
            self.N += 1

    def __getitem__(self, k):
        """Return the value associated with the given key `k`."""
        i = self._hash(k)
        while self._keys[i] is not None:
            if k == self._keys[i]:
                return self._vals[i]
            else:
                i = (i + 1) % self.M
        else:
            raise KeyError(k)

    def __delitem__(self, k):
        """Delete the item associated with `k`."""
        if not self.__contains__(k):
            raise KeyError(k)
        i = self._hash(k)
        # Set slot of `k` to None
        while k is not self._keys[i]:
            i = (i + 1) % self.M
        self._keys[i] = None
        self._vals[i] = None
        i = (i + 1) % self.M
        # Rehash all keys in the cluster to the right of the deleted key
        while self._keys[i] is not None:
            key_to_redo = self._keys[i]
            val_to_redo = self._vals[i]
            self._keys[i] = None
            self._vals[i] = None
            self.N -= 1
            self.__setitem__(key_to_redo, val_to_redo)
            i = (i + 1) % self.M
        self.N -= 1
        if self.N > 0 and self.N <= self.M/8:
            self._resize(self.M // 2)

    def __len__(self):
        return self.size

    def __contains__(self, k):
        """Return True if `k` is present in the table, False otherwise."""
        try:
            self.__getitem__(k)
            return True
        except KeyError:
            return False

    def __eq__(self, other):
        return sorted(self.items()) == sorted(other.items())

    def __str__(self):
        return str(self.items())

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __iter__(self):
        """Return an iterator of all of the keys in the table."""
        yield from self.keys()

    def keys(self):
        return [k for k in self._keys if k is not None]

    def values(self):
        return [v for (k, v) in zip(self._keys, self._vals) if k is not None]

    def items(self):
        return [(k, v) for (k, v) in zip(self._keys, self._vals) 
                if k is not None]


# -----------------------------------------------------------------------------
#         Run tests
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import types

    # Exercise 3.4.1
    keys = 'EASYQUTION'
    items = [(c, i) for i, c in enumerate(keys)]

    # Override _hash function with custom function
    def __hash(self, k):
        return 11*(ord(k) - ord('A')) % self.M

    # SeparateChainingHashST._hash = __hash    # class patching, all instances
    st = SeparateChainingHashST(M=5)
    st._hash = types.MethodType(__hash, st)  # instance patching
    for k, v in items:
        st[k] = v
    st._validate_size()

    # Test SeparateChainingLiteHashST
    stl = SeparateChainingLiteHashST(M=5)
    stl._hash = types.MethodType(__hash, stl)
    for k, v in items:
        stl[k] = v

    stl.delete_later_than(5)
    assert all([x.N_before <= 5 for x in stl._nodes()])

    # Test LinearProbingHashST
    stp = LinearProbingHashST(M=16)
    stp._hash = types.MethodType(__hash, stp)
    for k, v in items:
        stp[k] = v

    sts = LinearProbingHashST(M=10)
    sts._hash = types.MethodType(__hash, sts)
    for k, v in items:
        sts[k] = v

# =============================================================================
# =============================================================================
