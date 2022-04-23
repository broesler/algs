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

from algs.search.table import SequentialSearchST


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
    def __init__(self, items=None, M=7):
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

    def _hash(self, key):
        """Modular hashing using Python's built-in `hash` function."""
        # TODO `hash` is "salted" each time python is run for security reasons,
        # so results are non-deterministic. Manual override or set seed?
        return hash(key) % self.M

    def __getitem__(self, key):
        """Return the value associated with the given key `k`."""
        return self.st[self._hash(key)][key]

    def __setitem__(self, key, val):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`."""
        self.st[self._hash(key)][key] = val
        self.size += 1

    # Exercise 3.4.19
    def keys(self):
        pass


# -----------------------------------------------------------------------------
#         Run tests
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    keys = 'EASYQUTION'
    items = [(c, i) for i, c in enumerate(keys)]
    st = SeparateChainingHashST(items)

# =============================================================================
# =============================================================================
