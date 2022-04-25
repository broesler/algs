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

from algs.basics import Queue as _Queue
from algs.search.table import SequentialSearchST

__all__ = ['SeparateChainingHashST']


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
    def __init__(self, items=None, M=7, cache=False):
        self.M = M
        self.size = 0
        items = items or []  # must be iterable
        # Create M linked lists
        self.st = [SequentialSearchST() for _ in range(M)]
        # Initialize the symbol table
        try:
            for k, v in items:
                self.__setitem__(k, v)
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             'expects an iterable mapping input.')

    @property
    def is_empty(self):
        return self.size == 0

    def _hash(self, k):
        """Modular hashing using Python's built-in `hash` function."""
        # NOTE `hash` is "salted" each time python is run for security reasons,
        # so results are non-deterministic. Manual override or set seed?
        return hash(k) % self.M

    def _validate_size(self):
        """Check if `size` is self-consistent."""
        assert self.size == sum([t.size for t in self.st])

    # ------------------------------------------------------------------------- 
    #         Public API
    # -------------------------------------------------------------------------
    def __getitem__(self, k):
        """Return the value associated with the given key `k`."""
        return self.st[self._hash(k)][k]

    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`."""
        self.st[self._hash(k)][k] = v
        self.size += 1

    # Exercise 3.4.9
    def __delitem__(self, k):
        """Delete the item associated with `k`.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        del self.st[self._hash(k)][k]
        self.size -= 1

    def __contains__(self, k):
        """Return True if `k` is present in the table, False otherwise."""
        try:
            self.__getitem__(k)
            return True
        except KeyError:
            return False

    def __str__(self):
        return str(st.st)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

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

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
    def _make_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        def iterator(self, lo=None, hi=None):
            """Iterate over each symbol table."""
            q = list()
            for t in self.st:
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
    # Private class of key/value pairs
    class _Node():
        """Internal item object to hold key and value."""
        def __init__(self, key, value, next=None):
            self.key = key
            self.val = value
            self.next = next

        def __str__(self):
            return f"(key={repr(self.key)}, value={repr(self.val)})"

        def __repr__(self):
            return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __init__(self, items=None, M=7, cache=False):
        self.M = M
        self.size = 0
        items = items or []  # must be iterable
        self.st = M*[None]   # Create M linked lists
        # Initialize the symbol table
        try:
            for k, v in items:
                self.__setitem__(k, v)
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             'expects an iterable mapping input.')

    @property
    def is_empty(self):
        return self.size == 0

    def _hash(self, k):
        """Modular hashing using Python's built-in `hash` function."""
        return hash(k) % self.M

    # ------------------------------------------------------------------------- 
    #         Public API
    # -------------------------------------------------------------------------
    def __len__(self):
        return self.size

    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`."""
        x = self.st[self._hash(k)]
        while x:
            if k == x.key:
                x.val = v
                break
            else:
                x = x.next
        else:
            x = self._Node(k, v)
            self.size += 1

    def __getitem__(self, k):
        """Return the value associated with the given key `k`."""
        x = self.st[self._hash(k)]
        while x:
            if k == x.key:
                return v
            else:
                x = x.next
        else:
            raise KeyError(k)

    def __delitem__(self, k):
        """Delete the item associated with `k`."""
        x = self.st[self._hash(k)]
        if x is None:
            raise KeyError(k)

        while x.next:
            if k == x.next.key:
                x.next = x.next.next  # unlink the node
                self.size -= 1
                return
            else:
                x = x.next
        else:
            raise KeyError(k)

    def __contains__(self, k):
        """Return True if `k` is present in the table, False otherwise."""
        try:
            self.__getitem__(k)
            return True
        except KeyError:
            return False

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

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
    def _make_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        def iterator(self, lo=None, hi=None):
            """Iterate over each symbol table."""
            q = list()
            for t in self.st:
                x = t
                while x:
                    q.append(x.key if rtype == 'keys' else
                             (x.val if rtype == 'values' else (x.key, x.val)))
                    x = x.next
            return q
        return iterator


# -----------------------------------------------------------------------------
#         Run tests
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # Exercise 3.4.1
    keys = 'EASYQUTION'
    items = [(c, i) for i, c in enumerate(keys)]
    st = SeparateChainingHashST(M=5)

    # Override _hash function with custom function
    def __hash(self, k):
        return 11*(ord(k) - ord('A') + 1) % self.M

    SeparateChainingHashST._hash = __hash    # class patching of all instances
    # import types
    # st._hash = types.MethodType(__hash, st)  # instance patching
    for k, v in items:
        st[k] = v

# =============================================================================
# =============================================================================
