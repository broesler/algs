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

from algs.basics import RandomQueue
from algs.search.table import SymbolTable
from algs.search.hash import LinearProbingHashST
from algs.search.tree import BST
from algs.search.balanced_tree import RedBlackBST


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

    @abstractmethod
    def size(self):
        """Number of elements in the table."""
        pass

    @property
    def is_empty(self):
        return self.size() == 0

    @abstractmethod
    def add(k):
        """Add a key `k` to the set."""
        pass

    @abstractmethod
    def __delitem__(self, k):
        """Remove key `k` from the set."""
        pass

    @abstractmethod
    def __contains__(self, k):
        """Return True if `k` is present in the set, False otherwise."""
        pass

    # Aliased methods to match with Algorithms book API (see p 489)
    def delete(self, k):
        """Remove key `k` from the set."""
        return self.__delitem__(k)

    def contains(self, k):
        """Return True if `k` is present in the set, False otherwise."""
        return self.__contains__(k)

    # -------------------------------------------------------------------------
    #         Internal methods
    # -------------------------------------------------------------------------
    def __len__(self):
        return self.size()

    def __eq__(self, other):
        """Return True if each set contains the same keys."""
        return sorted(self) == sorted(other)

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


# TODO move these to an ABC and subclass it twice for OrderedSet and
# OrderedSymbolTable
class OrderedSet(UnorderedSet):
    # An abstract base class implementing an ordered set.
    @property
    @abstractmethod
    def _N(self):
        """Number of elements in the table."""
        pass

    def size(self, lo=None, hi=None):
        """Number of items in the table between keys `lo` and `hi`,
        inclusive."""
        if lo is None and hi is None:
            return self._N

        if lo is None:
            lo = self.min()
        if hi is None:
            hi = self.max()

        if lo > hi:
            return 0
        elif hi in self:
            return 1 + self.rank(hi) - self.rank(lo)
        else:
            return self.rank(hi) - self.rank(lo)

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

    @abstractmethod
    def keys(self, lo=None, hi=None):
        """Return an in-order list of the keys between the keys `lo` and `hi`,
        inclusive.

        Parameters
        ----------
        lo : key
            Minimum key over which to search, inclusive.
        hi : key
            Maximum key over which to search, inclusive.

        Returns
        -------
        q : list
            list of the keys between `lo` and `hi`, inclusive.
        """
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
        self._st = LinearProbingHashST()
        super().__init__(keys)

    def size(self):
        return self._st.size()

    def add(self, k):
        self._st.__setitem__(k, v=None)

    def __delitem__(self, k):
        self._st.__delitem__(k)

    def __contains__(self, k):
        return k in self._st

    def __iter__(self):
        yield from self._st.keys()


# Exercise 3.5.1
class Set(OrderedSet):
    __doc__ = f"""Implements an ordered set using a wrapper on a red-black BST.
               {OrderedSet.__doc__}
               """

    def __init__(self, keys=None):
        self._st = RedBlackBST()
        super().__init__(keys)

    @property
    def _N(self):
        return self._st._N

    def add(self, k):
        self._st.__setitem__(k, v=None)

    def __delitem__(self, k):
        self._st.__delitem__(k)

    def __contains__(self, k):
        return k in self._st

    def __iter__(self):
        yield from self._st.keys()

    def keys(self, lo=None, hi=None):
        return self._st.keys(lo, hi)

    # -------------------------------------------------------------------------
    #         Ordered methods
    # -------------------------------------------------------------------------
    def min(self):
        return self._st.min()

    def max(self):
        return self._st.max()

    def floor(self, k):
        return self._st.floor(k)

    def ceil(self, k):
        return self._st.ceil(k)

    def rank(self, k):
        return self._st.rank(k)

    def select(self, r):
        return self._st.select(r)

    def delete_min(self):
        return self._st.delete_min()

    def delete_max(self):
        return self._st.delete_max()


# Exercise 3.5.8
class MultiValHashST(LinearProbingHashST):
    __doc__ = f"""Implements a hash table using arrays with linear probing, but
               allows multiple values to be associated with each key.

               .. note::
                   `ST.get` will return any value associated with a key `k`.
                   `ST.delete` will delete all keys equal to `k`.
               {SymbolTable.__doc__}"""

    def _resize(self, M):
        """Resize the internal keys and values arrays."""
        # Create a new table and hash the existing keys into it
        t = self.__class__(M=M, resize=True)
        for k, v in zip(self._keys, self._vals):
            if k is not None:
                for x in v:  # iterate over the queue
                    t[k] = x
        # Use those new arrays in *self*
        self._keys = t._keys
        self._vals = t._vals
        self.M = t.M

    def __setitem__(self, k, v):
        if not self._RESIZE_FLAG and self.N == self.M:
            raise RuntimeError(("Trying to insert into a full table! "
                                "Set `resize=True`."))

        if self._RESIZE_FLAG and self.N >= self.M // 2:
            self._resize(2*self.M)
            self._lgM += 1

        i = self._hash(k)
        self._cost = 1
        while self._keys[i] is not None:
            if k == self._keys[i]:
                self._vals[i].enqueue(v)
                return
            else:
                i = (i + 1) % self.M
                self._cost += 1
        else:
            # Put a new key in the table
            self._keys[i] = k
            self._vals[i] = RandomQueue()  # keep a list of values for each key
            self._vals[i].enqueue(v)
            self.N += 1

    def __getitem__(self, k):
        i = self._hash(k)
        self._cost = 1
        while self._keys[i] is not None:
            if k == self._keys[i]:
                return self._vals[i].sample()  # return *any* value
            else:
                i = (i + 1) % self.M
                self._cost += 1
        else:
            raise KeyError(k)


# Exercise 3.8.9
class MultiValBST(BST):
    """Implements a binary search tree, but allows multiple values to be
    associated with each key."""

    class _Node(BST._Node):
        def __init__(self, key, value=None):
            super().__init__(key, value)
            self.val = RandomQueue()  # store all values in a queue
            self.val.enqueue(value)

    @staticmethod
    def _return_func(x):
        return x.val.sample()  # return *any* value

    @staticmethod
    def _set_func(x, v):
        x.val.enqueue(v)


# Exercise 3.8.10
class MultiValRedBlackBST(RedBlackBST):
    """Implements a balanced binary search tree, but allows multiple values to
    be associated with each key."""

    class _Node(RedBlackBST._Node):
        def __init__(self, key, value, *args, **kwargs):
            super().__init__(key, value, *args, **kwargs)
            self.val = RandomQueue()  # store all values in a queue
            self.val.enqueue(value)

    @staticmethod
    def _return_func(x):
        return x.val.sample()  # return *any* value

    @staticmethod
    def _set_func(x, v):
        x.val.enqueue(v)


# TODO test_multiset
if __name__ == '__main__':
    from algs.exercises.draw_tree import TreeArtist

    # Exercise 3.5.8
    EXPECT_STR = 'SEARCHEXAMPLE'
    items = list((c, i) for i, c in enumerate(EXPECT_STR))
    st = MultiValHashST(items)
    st['X'] = [1, 2, 3]
    st['Y'] = [1, 2, 3]
    st['Y'] = 4
    st['A'] = 'hello'
    assert st['A'] in [2, 8, 'hello']
    assert st['E'] in [1, 6, 12]
    print('---MultiValHashST---')
    print(st)
    del st['E']
    assert 'E' not in st
    print(st)

    # Exercise 3.5.9
    keys = list('SEARCHEXAMPLE')
    items = list((c, i) for i, c in enumerate(keys))
    t = BST(items)
    TreeArtist(t).draw(fignum=1, label_vals=True)

    print('---MultiValBST---')
    st = MultiValBST(items)
    st['X'] = [1, 2, 3]
    st['Y'] = [1, 2, 3]
    st['Y'] = 4
    st['A'] = 'hello'
    TreeArtist(st).draw(fignum=2, label_vals=True)
    assert st['A'] in [2, 8, 'hello']
    assert st['E'] in [1, 6, 12]
    print(st)
    del st['E']
    assert 'E' not in st

    # Exercise 3.5.10
    keys = list('SEARCHEXAMPLE')
    items = list((c, i) for i, c in enumerate(keys))
    t = RedBlackBST(items)
    TreeArtist(t).draw(fignum=3, label_vals=True)

    print('---MultiValRedBlackBST---')
    st = MultiValRedBlackBST(items)
    st['X'] = [1, 2, 3]
    st['Y'] = [1, 2, 3]
    st['Y'] = 4
    st['A'] = 'hello'
    TreeArtist(st).draw(fignum=4, label_vals=True)
    assert st['A'] in [2, 8, 'hello']
    assert st['E'] in [1, 6, 12]
    print(st)
    del st['E']
    assert 'E' not in st

# =============================================================================
# =============================================================================
