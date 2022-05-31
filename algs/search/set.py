#!/usr/bin/env python3
# =============================================================================
#     File: set.py
#  Created: 2022-05-30 19:34
#   Author: Bernie Roesler
#
"""
Implements Set and HashSet APIs using symbol tables. See §3.5.
"""
# =============================================================================

from abc import ABC, abstractmethod
from algs import RedBlackBST, LinearProbingHashST


class UnorderedSet(ABC):
    # An abstract base class for unordered sets of keys.
    """
    Attributes
    ----------
    size : int
        Number of keys in the set.
    is_empty : bool
        True if `size == 0`.
    """

    def __init__(self, keys=None):
        """
        Parameters
        ----------
        keys : list, optional
            Iterable of keys to be put into the set.
        """
        keys = keys or []
        for k in keys:
            self.add(k)

    @property
    @abstractmethod
    def size(self):
        """Number of elements in the table."""
        pass

    def __len__(self):
        return self.size

    @property
    def is_empty(self):
        return self.size == 0

    @abstractmethod
    def add(self, k):
        """Add a key to the set."""
        pass

    @abstractmethod
    def __delitem__(self, k):
        """Remove key from the set."""
        pass

    def __contains__(self, k):
        """Return True if `k` is present in the set, False otherwise."""
        try:
            self.__getitem__(k)
            return True
        except KeyError:
            return False

    # Aliased methods to match with Algorithms book API (see p 489)
    def delete(self, k):
        return self.__delitem__(k)

    def contains(self, k):
        return self.__contains__(k)

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    @abstractmethod
    def __iter__(self):
        """Return an iterator of all of the keys in the set.

        Yields
        ------
        keys : iterable of keys
        """
        pass


# Exercise 3.5.1
class HashSet(UnorderedSet):
    __doc__ = f"""Implements an unordered set using a wrapper on a linear probing hash
               table.
               {UnorderedSet.__doc__}
               """

    def __init__(self, keys=None):
        self.st = LinearProbingHashST()
        super().__init__(keys)

    @property
    def size(self):
        return self.st.size

    def add(self, k):
        self.st.__setitem__(k, v=None)

    def __delitem__(self, k):
        self.st.__delitem__(k)

    def __iter__(self):
        yield from self.st.keys()


# TODO move to tests/test_search.py
if __name__ == "__main__":
    keys = list('abcde')
    a = HashSet(keys)
    assert sorted(a) == keys
    a.add('x')
    assert sorted(a) == list('abcdex')
    a.delete('d')
    assert sorted(a) == list('abcex')

# =============================================================================
# =============================================================================
