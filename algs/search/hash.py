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
