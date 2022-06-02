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

from algs.basics import Bag
from algs.search.table import SymbolTable, OrderedMethods
from algs.search.hash import LinearProbingHashST
from algs.search.tree import BST
from algs.search.balanced_tree import RedBlackBST

__all__ = ['UnorderedSet', 'OrderedSet', 'MultiValHashST',
           'MultiValRedBlackBST', 'MultiKeyHashST', 'MultiKeyRedBlackBST',
           'invert']


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
        keys : iterable, optional
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


class OrderedSet(OrderedMethods, UnorderedSet):
    # An abstract base class implementing an ordered set.
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
                for x in v:  # iterate over multiple values
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
                self._vals[i].add(v)
                return
            else:
                i = (i + 1) % self.M
                self._cost += 1
        else:
            # Put a new key in the table
            self._keys[i] = k
            self._vals[i] = Bag()  # keep a list of values for each key
            self._vals[i].add(v)
            self.N += 1


class MultiValBST(BST):
    """Implements a binary search tree, but allows multiple values to be
    associated with each key."""

    class _Node(BST._Node):
        def __init__(self, key, value=None):
            super().__init__(key, value)
            self.val = Bag()  # store all values in a queue
            self.val.add(value)

    @staticmethod
    def _set_func(x, v):
        x.val.add(v)


class MultiValRedBlackBST(RedBlackBST):
    """Implements a balanced binary search tree, but allows multiple values to
    be associated with each key."""

    class _Node(RedBlackBST._Node):
        def __init__(self, key, value, *args, **kwargs):
            super().__init__(key, value, *args, **kwargs)
            self.val = Bag()  # store all values in a queue
            self.val.add(value)

    @staticmethod
    def _set_func(x, v):
        x.val.add(v)


# Exercise 3.5.8
class MultiKeyHashST(LinearProbingHashST):
    __doc__ = f"""Implements a hash table using arrays with linear probing, but
               allows multiple keys.

               .. note::
                   `ST.get` will return *any* value associated with a key `k`.
                   `ST.delete` will delete *all* keys equal to `k`.
               {SymbolTable.__doc__}"""

    def __setitem__(self, k, v):
        """Associate value `v` with key `k`. Multiple identical keys are
        allowed."""
        if not self._RESIZE_FLAG and self.N == self.M:
            raise RuntimeError(("Trying to insert into a full table! "
                                "Set `resize=True`."))

        if self._RESIZE_FLAG and self.N >= self.M // 2:
            self._resize(2*self.M)
            self._lgM += 1

        i = self._hash(k)
        self._cost = 1
        while self._keys[i] is not None:
            # No check for self._keys[i] == k, since we allow multiple keys
            i = (i + 1) % self.M
            self._cost += 1
        else:
            self._keys[i] = k
            self._vals[i] = v
            self.N += 1

    def __delitem__(self, k):
        """Delete all instances of `k` from the table."""
        if k not in self:
            raise KeyError(k)

        # Set slot of first instance of `k` to None
        i = self._hash(k)
        _cost = 1
        while k != self._keys[i]:
            i = (i + 1) % self.M
            _cost += 1
        self._keys[i] = None
        self._vals[i] = None

        # Rehash all keys in the cluster to the right of the deleted key
        i = (i + 1) % self.M
        while self._keys[i] is not None:
            key_to_redo = self._keys[i]
            val_to_redo = self._vals[i]
            self._keys[i] = None
            self._vals[i] = None
            self.N -= 1
            # Do not re-hash multiple instances of the key to be deleted
            if k != key_to_redo:
                self.__setitem__(key_to_redo, val_to_redo)
                _cost += self._cost
            i = (i + 1) % self.M

        # Update counters
        self.N -= 1
        self._cost = _cost
        # Check for a resize if table is small enough
        if self._RESIZE_FLAG and (self.N > 0 and self.N <= self.M // 8):
            self._resize(self.M // 2)
            self._lgM -= 1


# Exercise 3.5.9
class MultiKeyBST(BST):
    __doc__ = f"""Implements a binary search tree, but allows multiple keys.
        {BST._attribs_doc}
        """

    def __delitem__(self, k):
        """Delete all instances of `k` from the table."""
        while k in self:
            self._root = self._delete(k, self._root)
            if self._CACHE_FLAG and self._cache and k == self._cache.key:
                self._cache = None

    def _set(self, k, v, x=None):
        # subtree is empty, create a new node
        if x is None:
            h = self._Node(k, v)
            if self._CACHE_FLAG:
                self._cache = h
            return h

        # create a child, or update the value
        self._cost += 1
        if k < x.key:
            x.left = self._set(k, v, x.left)
        else:  # k > x.key or k == x.key
            # Always go right for duplicate keys
            x.right = self._set(k, v, x.right)

        self._update_node(x)
        return x


# Exercise 3.5.10
class MultiKeyRedBlackBST(RedBlackBST):
    __doc__ = f"""Implements a red-black binary search tree, but allows
        multiple keys.
        {BST._attribs_doc}
        """

    def __delitem__(self, k):
        """Delete all instances of `k` from the table."""
        if not self.__contains__(k):
            raise KeyError(k)
        while k in self:
            # If root is a 2-node, make it a 3-node
            if (not self._is_red(self._root.left) and
                    not self._is_red(self._root.right)):
                self._root.color = self._RED
            self._root = self._delete(k, self._root)
            if self._CACHE_FLAG and self._cache and k == self._cache.key:
                self._cache = None

    def _set(self, k, v, h=None):
        # subtree is empty, create a new node with a red link to parent
        if h is None:
            x = self._Node(k, v, color=self._RED)
            if self._CACHE_FLAG:
                self._cache = x
            return x

        # create a child, or update the value
        self._cost += 1
        if k < h.key:
            h.left = self._set(k, v, h.left)
        else:  # k > h.key or k == h.key
            # Always go right for duplicate keys
            h.right = self._set(k, v, h.right)

        # Balance the tree (red links left-leaning)
        if self._is_red(h.right) and not self._is_red(h.left):
            h = self._rotate_left(h)
        if self._is_red(h.left) and self._is_red(h.left.left):
            h = self._rotate_right(h)
        # Split a 4-node into 3 2-nodes
        if self._is_red(h.right) and self._is_red(h.left):
            self._flip_colors(h)

        # Update node attributes
        self._update_node(h)
        return h


def invert(st):
    """Given a multi-valued symbol table, return the inverted index."""
    ts = MultiValHashST()
    for k, vals in st.items():
        for v in vals:
            ts[v] = k
    return ts


# TODO test_multiset
if __name__ == '__main__':
    from algs.exercises.draw_tree import TreeArtist

    keys = list('SEARCHEXAMPLE')
    items = list((c, i) for i, c in enumerate(keys))

    print('---MultiValHashST---')
    st = MultiValHashST(items)
    st['X'] = [1, 2, 3]
    st['Y'] = [4, 5, 6]
    st['Y'] = 4
    st['A'] = 'hello'
    assert list(st['A']) == [2, 8, 'hello']
    assert list(st['E']) == [1, 6, 12]
    print(st)
    del st['E']
    assert 'E' not in st
    print(st)

    t = BST(items)
    # TreeArtist(t).draw(fignum=1, label_vals=True)

    print('---MultiValBST---')
    st = MultiValBST(items)
    st['X'] = [1, 2, 3]
    st['Y'] = [4, 5, 6]
    st['Y'] = 4
    st['A'] = 'hello'
    # TreeArtist(st).draw(fignum=2, label_vals=True)
    assert list(st['A']) == [2, 8, 'hello']
    assert list(st['E']) == [1, 6, 12]
    print(st)
    del st['E']
    assert 'E' not in st

    t = RedBlackBST(items)
    # TreeArtist(t).draw(fignum=3, label_vals=True)

    print('---MultiValRedBlackBST---')
    st = MultiValRedBlackBST(items)
    st['X'] = [1, 2, 3]
    st['Y'] = [4, 5, 6]
    st['Y'] = 4
    st['A'] = 'hello'
    # TreeArtist(st).draw(fignum=4, label_vals=True)
    assert list(st['A']) == [2, 8, 'hello']
    assert list(st['E']) == [1, 6, 12]
    print(st)
    del st['E']
    assert 'E' not in st

    # Exercise 3.5.8
    print('---MultiKeyHashST---')
    st = MultiKeyHashST(items)
    st['X'] = [1, 2, 3]
    st['Y'] = [4, 5, 6]
    st['Y'] = 4
    st['A'] = 'hello'
    assert st['A'] in [2, 8, 'hello']
    assert st['E'] in [1, 6, 12]
    print(st)
    del st['E']
    assert 'E' not in st
    print(st)

    # Exercise 3.5.9 -- multiple keys
    print('---MultiKeyBST---')
    st = MultiKeyBST(items)
    st['X'] = [1, 2, 3]
    st['Y'] = [4, 5, 6]
    st['Y'] = 4
    st['A'] = 'hello'
    # TreeArtist(st).draw(fignum=5, label_vals=True)
    assert st['A'] in [2, 8, 'hello']
    assert st['E'] in [1, 6, 12]
    print(st)
    del st['E']
    assert 'E' not in st
    print(st)
    # TreeArtist(st).draw(fignum=6, label_vals=True)

    # Exercise 3.5.9 -- multiple keys
    print('---MultiKeyRedBlackBST---')
    st = MultiKeyRedBlackBST(items)
    st['X'] = [1, 2, 3]
    st['Y'] = [4, 5, 6]
    st['Y'] = 4
    st['A'] = 'hello'
    TreeArtist(st).draw(fignum=7, label_vals=True)
    assert st['A'] in [2, 8, 'hello']
    assert st['E'] in [1, 6, 12]
    print(st)
    del st['E']
    assert 'E' not in st
    print(st)
    TreeArtist(st).draw(fignum=8, label_vals=True)

    # Test invert
    st = MultiValHashST(items)
    ts = invert(st)
    assert st == invert(ts)
    assert ts == invert(st)

# =============================================================================
# =============================================================================
