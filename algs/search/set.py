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


# ----------------------------------------------------------------------------- 
#         Define Abstract Base Classes
# -----------------------------------------------------------------------------
class UnorderedSet(ABC):
    # An abstract base class for unordered sets of keys. Note that a set does
    # not contain a `__setitem__`  or `__getitem__` method, since we do not
    # associate values with the keys.
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

    # TODO implement 2 argument version with lo and hi keys.
    @property
    @abstractmethod
    def size(self):
        """Number of elements in the table."""
        pass

    @property
    def is_empty(self):
        return self.size == 0

    @abstractmethod
    def add(k):

        """Add a key to the set."""
        pass

    @abstractmethod
    def __delitem__(self, k):
        """Remove key from the set."""
        pass

    @abstractmethod
    def __contains__(self, k):
        """Return True if `k` is present in the set, False otherwise."""
        pass

    # Aliased methods to match with Algorithms book API (see p 489)
    def delete(self, k):
        return self.__delitem__(k)

    def contains(self, k):
        return self.__contains__(k)

    # ------------------------------------------------------------------------- 
    #         Internal methods
    # -------------------------------------------------------------------------
    def __len__(self):
        return self.size

    def __str__(self):
        return '{' + ', '.join([repr(k) for k in self]) + '}'

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    @abstractmethod
    def __iter__(self):
        """Return an iterator over all of the keys in the set.

        Yields
        ------
        keys : iterable of keys
        """
        pass


class OrderedSet(UnorderedSet):
    # An abstract base class implementing an ordered set.
    @abstractmethod
    def min(self):
        """Return the minimum key in the set."""
        pass

    @abstractmethod
    def max(self):
        """Return the maximum key in the set."""
        pass

    @abstractmethod
    def floor(self, k):
        """Return the largest key less than or equal to `k`, or None if `k` is
        less than the smallest key in the set.
        """
        pass

    @abstractmethod
    def ceil(self, k):
        """Return the smallest key greater than or equal to `k`, or None if `k`
        is greater than the largest key in the set.
        """
        pass

    @abstractmethod
    def rank(self, k):
        """Return the number of keys strictly less than `k`."""
        pass

    @abstractmethod
    def select(self, r):
        """Return the key of rank `r`.

        Raises
        ------
        IndexError
            If there are fewer than `r`+1 keys in the set.
        """
        pass

    @abstractmethod
    def delete_min(self):
        """Delete the minimum key in the set."""
        pass

    @abstractmethod
    def delete_max(self):
        """Delete the maximum key in the set."""
        pass


# ----------------------------------------------------------------------------- 
#         Concrete Classes
# -----------------------------------------------------------------------------
# Exercise 3.5.1
class HashSet(UnorderedSet):
    __doc__ = f"""Implements an unordered set using a wrapper on a linear
               probing hash table.
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

    def __contains__(self, k):
        return k in self.st

    def __iter__(self):
        yield from self.st.keys()


class Set(OrderedSet):
    __doc__ = f"""Implements an ordered set using a wrapper on a red-black BST.
               {OrderedSet.__doc__}
               """

    def __init__(self, keys=None):
        self.st = RedBlackBST()
        super().__init__(keys)

    @property
    def size(self):
        return self.st.size

    def add(self, k):
        self.st.__setitem__(k, v=None)

    def __delitem__(self, k):
        self.st.__delitem__(k)

    def __contains__(self, k):
        return k in self.st

    def __iter__(self):
        yield from self.st.keys()

    # Ordered methods
    def min(self):
        return self.st.min()

    def max(self):
        return self.st.max()

    def floor(self, k):
        return self.st.floor(k)

    def ceil(self, k):
        return self.st.ceil(k)

    def rank(self, k):
        return self.st.rank(k)

    def select(self, r):
        return self.st.select(r)

    def delete_min(self):
        return self.st.delete_min()

    def delete_max(self):
        return self.st.delete_max()


# TODO move to tests/test_search.py
if __name__ == "__main__":
    keys = list('abcde')
    a = HashSet(keys)
    assert sorted(a) == keys
    a.add('x')
    assert sorted(a) == list('abcdex')
    a.delete('d')
    assert sorted(a) == list('abcex')

    t = Set(keys)
    assert sorted(t) == keys
    t.add('x')
    assert sorted(t) == list('abcdex')
    t.delete('d')
    assert sorted(t) == list('abcex')
    assert t.min() == 'a'


# =============================================================================
# =============================================================================
