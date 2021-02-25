#!/usr/bin/env python3
# =============================================================================
#     File: search.py
#  Created: 2019-11-01 19:50
#   Author: Bernie Roesler
#
"""
  Description: Search algorithms
"""
# =============================================================================

import random  # only needed for Ex 3.2.42 (deletion methods)

from algs.basics import Stack as _Stack, \
                        Queue as _Queue, \
                        _empty_check
from algs.sort import mergesort as _mergesort

__all__ = ['SequentialSearchST', 'BinarySearchST', 'BST', 'BST_nr',
           'ThreadedST', 'ThreadedST_nr']

# TODO
#   * make ST(ABC) out of MutableMapping? to hold things like `size`,
#     `is_empty`, `__len__` for all?
#   * implement `clear`, `copy`, `get`, `popitem`, `__reverse__`,
#     `setdefault`, and `update` like true dictionaries
#   * implement `t.put(k, v)` method instead of just t[k] = v assignment
#   * use collections.abc.[Keys|Values|Items]View classes?


# Private class of key/value pairs
class _Item():
    """Internal item object to hold key and value."""
    def __init__(self, key, value):
        self.key = key
        self.val = value

    def __str__(self):
        return f"(key={repr(self.key)}, value={repr(self.val)})"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"


class SequentialSearchST():
    """Implements an unordered symbol table with a linked list.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) pairs to be put into the table.

    Attributes
    ----------
    size : int
        Number of items in the table.
    is_empty : bool
        True if `size == 0`.

    .. note:: SequentialSearchST lacks methods like `min`/`max`,
        `floor`/`ceil`, etc. that the ordered symbol tables (BinarySearchST,
        BST, etc.) can efficiently implement.
    """
    # Custom item for singly-linked list
    class _Item(_Item):
        def __init__(self, key, value, next=None):
            super().__init__(key, value)
            self.next = next  # pointer to next item

    # Initialize the symbol table
    def __init__(self, items=list(), cache=False):
        self.size = 0             # number of elements in the table
        self._first = None
        self._cost = 0            # cost of previous get/put/delete
        self._CACHE_FLAG = cache
        self._cache = None        # store latest search hit

        # Initialize the symbol table
        try:
            for k, v in items:
                self.__setitem__(k, v)
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} expects a `list` of tuples input.")

    @property
    def is_empty(self):
        return self.size == 0

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __len__(self):
        return self.size

    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`."""
        # Check the cache (Ex 3.1.25)
        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            self._cache.val = v
            return

        # Perform sequential search
        x = self._first
        i = 0
        while x:
            if k == x.key:
                self._cost = i + 1
                x.val = v              # key exists, so update value
                if self._CACHE_FLAG:
                    self._cache = x
                return
            else:
                i += 1
                x = x.next
        else:
            self._cost = self.size   # tested all the keys!
            item = self._Item(k, v, self._first)  # add new key to beginning of list: O(1)
            self._first = item
            self.size += 1
            if self._CACHE_FLAG:
                self._cache = self._first  # update the cache

    def __getitem__(self, k):
        """Return the value associated with the given key `k`."""
        # Check the cache
        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            return self._cache.val

        # Perform sequential search
        x = self._first
        i = 0
        while x:
            if k == x.key:
                self._cost = i + 1
                if self._CACHE_FLAG:
                    self._cache = x
                return x.val
            else:
                i += 1
                x = x.next
        else:
            self._cost = self.size  # tested all the keys!
            raise KeyError(k)

    # Exercise 3.1.5
    def __delitem__(self, k):
        """Delete the item associated with `k`.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        # Perform sequential search
        x = self._first

        # Check the first node
        if k == x.key:
            self._cost = 1
            # Clear the cache and remove the item
            if self._CACHE_FLAG and self._cache and k == self._cache.key:
                self._cache = None
            self._first = x.next
            return

        # Search
        i = 0
        while x.next:
            if k == x.next.key:
                self._cost = i + 1
                # Clear the cache and remove the item
                if self._CACHE_FLAG and self._cache and k == self._cache.key:
                    self._cache = None
                x.next = x.next.next  # unlink the node
                return
            else:
                i += 1
                x = x.next
        else:
            self._cost = self.size
            raise KeyError(k)

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

    # -------------------------------------------------------------------------
    #         Iterator functions
    # -------------------------------------------------------------------------
    _docstring = """Return an in-order iterator over the {rtype}`.

    Returns
    -------
    q : iterator
        iterator over the {rtype}.
    """

    def keys(self):
        return self._make_inorder_iterator(rtype='keys')(self)

    def values(self):
        return self._make_inorder_iterator(rtype='values')(self)

    def items(self):
        return self._make_inorder_iterator(rtype='items')(self)

    keys.__doc__   = _docstring.format(rtype='keys')
    values.__doc__ = _docstring.format(rtype='values')
    items.__doc__  = _docstring.format(rtype='items')

    def __iter__(self):
        """Return an iterator of all of the keys in the table."""
        yield from self.keys()

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
    def _make_inorder_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        def iterator(self, lo=None, hi=None):
            """Iterate over items."""
            q = _Queue()
            x = self._first
            while x:
                q.enqueue(x.key if rtype == 'keys' else
                          (x.val if rtype == 'values' else (x.key, x.val)))
                x = x.next
            return list(q)
        return iterator


# Ex 3.1.2 unordered search with an array
class ArrayST():
    """Implements an unordered symbol table with an array.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) pairs to be put into the table.

    Attributes
    ----------
    size : int
        Number of items in the table.
    is_empty : bool
        True if `size == 0`.

    .. note:: ArrayST lacks methods like `min`/`max`,
        `floor`/`ceil`, etc. that the ordered symbol tables (BinarySearchST,
        BST, etc.) can efficiently implement.
    """
    def __init__(self, items=list(), cache=False, selforg=False):
        self._items = list()           # Ex 3.1.2 (ArrayST)
        self._cost = 0                 # cost of previous get/put/delete
        self._CACHE_FLAG = cache
        self._cache = None             # store latest search hit
        self._SELF_ORG_FLAG = selforg  # reorganize most recent results

        # Initialize the symbol table
        try:
            for k, v in items:
                self.__setitem__(k, v)
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} expects a `list` of tuples input.")

    @property
    def size(self):
        return len(self._items)

    @property
    def is_empty(self):
        return self.size == 0

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __len__(self):
        return self.size

    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`."""
        # Check the cache (Ex 3.1.25)
        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            self._cache.val = v
            return

        # Perform sequential search
        for i, item in enumerate(self._items):
            if k == item.key:
                self._cost = i + 1
                item.val = v              # key exists, so update value
                if self._CACHE_FLAG:
                    self._cache = self._items[i]
                # Ex 3.1.22
                if self._SELF_ORG_FLAG and i > 0:
                    # Move search hit to front of the list: O(n)
                    # Cost of pop (n - (i+1)) + cost of insert(0) (n - 1)
                    self._cost += 2*self.size - i - 2
                    self._items.insert(0, self._items.pop(i))
                return
        else:
            self._cost = self.size          # tested all the keys!
            self._items.append(_Item(k, v))  # add new key to end of list: O(1)
            if self._CACHE_FLAG:
                self._cache = self._items[-1]  # update the cache

    def __getitem__(self, k):
        """Return the value associated with the given key `k`."""
        # Check the cache
        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            return self._cache.val

        # Perform sequential search
        for i, item in enumerate(self._items):
            if k == item.key:
                self._cost = i + 1
                if self._CACHE_FLAG:
                    self._cache = self._items[i]
                if self._SELF_ORG_FLAG and i > 0:
                    # Move search hit to front of the list: O(n)
                    self._cost += 2*self.size - i - 2
                    self._items.insert(0, self._items.pop(i))
                return item.val
        else:
            self._cost = self.size  # tested all the keys!
            raise KeyError(k)

    # Exercise 3.1.5
    def __delitem__(self, k):
        """Delete the item associated with `k`.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        # Perform sequential search
        for i, item in enumerate(self._items):
            if k == item.key:
                self._cost = i + 1
                # Clear the cache and remove the item
                if self._CACHE_FLAG and self._cache and k == self._cache.key:
                    self._cache = None
                del self._items[i]
                return
        else:
            self._cost = self.size
            raise KeyError(k)

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
        return str(self._items)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Iterator methods
    # -------------------------------------------------------------------------
    def keys(self):
        """Return an iterator of all of the keys in the table."""
        return [x.key for x in self._items]

    def values(self):
        """Return an iterator of all of the values in the table."""
        return [x.val for x in self._items]

    def items(self):
        """Return an iterator of all of the items in the table."""
        return [(x.key, x.val) for x in self._items]

    def __iter__(self):
        """Return an iterator of all of the keys in the table."""
        yield from self.keys()


# Ex 3.1.12(a) Implement BST as an array of key/val objects. The original book
# implementation uses two parallel arrays for keys and values.
class BinarySearchST():
    """Implements an ordered-array with binary search symbol table.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) pairs to be put into the table.

    Attributes
    ----------
    size : int
        Number of items in the table.
    is_empty : bool
        True if `size == 0`.
    """
    def __init__(self, items=list(), cache=False):
        self._items = list()
        self._cost = 0              # track number of compares + array accesses
        self._CACHE_FLAG = cache
        self._cache = None
        # Initialize the symbol table
        try:
            # Ex 3.1.12(b) sort by keys so we get O(N log N) construction vs O(N^2)
            for k, v in _mergesort(items):
                self.__setitem__(k, v)
            self._assert_integrity()
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} expects a `list` of tuples input.")

    @property
    def size(self):
        return len(self._items)

    @property
    def is_empty(self):
        return self.size == 0

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __len__(self):
        return self.size

    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`.
        """
        # Ex 3.1.25 Check the cache
        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            self._cache.val = v
            return

        # Ex 3.1.28 If key is largest in table, slap it on the end! This
        # feature makes construction with a sorted list O(n).
        if not self.is_empty and k > self.max():
            self._items.append(_Item(k, v))

        # Perform binary search O(log2 N)
        i = self.rank(k)
        # if key is in the table, update the value
        if i < self.size and self._items[i].key == k:
            self._cost += 1
            self._items[i].val = v
        else:
            # create new Item in the table
            self._cost += self.size - i  # Θ(n-i) to move list elements
            self._items.insert(i, _Item(k, v))

        if self._CACHE_FLAG:
            self._cache = self._items[i]  # update the cache
        # self._assert_integrity()

    def __getitem__(self, k):
        """Return the value associated with the given key `k`.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        # See if we have cached the key
        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            return self._cache.val

        i = self.rank(k)
        if i < self.size and self._items[i].key == k:
            if self._CACHE_FLAG:
                self._cache = self._items[i]  # cache its location
            return self._items[i].val
        else:
            raise KeyError(k)

    def __delitem__(self, k):
        """Delete the item associated with `k`.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        i = self.rank(k)
        if i < self.size and self._items[i].key == k:
            # Clear cache of item if necessary
            if self._CACHE_FLAG and self._cache and k == self._cache.key:
                self._cache = None
            # Delete the item from the symbol table
            del self._items[i]
            return
        else:
            raise KeyError(k)
        # self._assert_integrity()

    def __contains__(self, k):
        """Return True if `k` is present in the table, False otherwise."""
        try:
            self.__getitem__(k)
            return True
        except KeyError:
            return False

    def __eq__(self, other):
        return self.items() == sorted(other.items())

    def __str__(self):
        return str(dict(self._items))

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    def min(self):
        """Return the minimum key in the table.

        Raises
        ------
        KeyError
            If the table is empty.
        """
        _empty_check(self)
        return self._items[0].key

    def max(self):
        """Return the maximum key in the table.

        Raises
        ------
        KeyError
            If the table is empty.
        """
        _empty_check(self)
        return self._items[-1].key

    def floor(self, k):
        """Return the largest key less than or equal to `k`, or None if `k` is
        less than the smallest key in the table.
        """
        i = self.rank(k)
        if i < self.size and self._items[i].key == k:
            return self._items[i].key
        elif i > 0:
            return self._items[i-1].key
        else:
            return None

    def ceil(self, k):
        """Return the smallest key greater than or equal to `k`, or None if `k`
        is greater than the largest key in the table.
        """
        i = self.rank(k)
        if i < self.size:
            return self._items[i].key
        else:
            return None

    def rank(self, k):
        """Return the number of keys strictly less than `k`."""
        # Non-recursive binary search algorithm
        self._cost = 0
        lo = 0
        hi = self.size - 1
        while lo <= hi:
            mid = (hi + lo) // 2
            self._cost += 2  # count 1 compare + 1 access here for simplicity
            if k < self._items[mid].key:
                hi = mid - 1
            elif k > self._items[mid].key:
                lo = mid + 1
            else:
                return mid
        return lo

    def select(self, r):
        """Return the key of rank `r`.

        Raises
        ------
        IndexError
            If there are fewer than `r`+1 keys in the table.
        """
        if 0 <= r < self.size:
            return self._items[r].key
        else:
            raise IndexError(r)

    def delete_min(self):
        """Delete the smallest key.

        Raises
        ------
        KeyError
            If the table is empty.
        """
        _empty_check(self)
        if self._CACHE_FLAG and self._cache is self._items[0]:
            self._cache = None
        del self._items[0]
        # self._assert_integrity()

    def delete_max(self):
        """Delete the largest key.

        Raises
        ------
        KeyError
            If the table is empty.
        """
        _empty_check(self)
        if self._CACHE_FLAG and self._cache is self._items[-1]:
            self._cache = None
        del self._items[-1]
        # self._assert_integrity()

    # -------------------------------------------------------------------------
    #         Iterator functions
    # -------------------------------------------------------------------------
    _docstring = """Return an in-order iterator over the {rtype} between the keys `lo`
    and `hi`, inclusive. Guaranteed to be the same order as `BST.keys()`.

    Parameters
    ----------
    lo : key
        Minimum key over which to search, inclusive.
    hi : key
        Maximum key over which to search, inclusive.

    Returns
    -------
    q : iterator
        iterator over the {rtype} between `lo` and `hi`, inclusive.
    """

    def keys(self, lo=None, hi=None):
        func = self._make_inorder_iterator(rtype='keys')
        return func(self, lo, hi)

    def values(self, lo=None, hi=None):
        func = self._make_inorder_iterator(rtype='values')
        return func(self, lo, hi)

    def items(self, lo=None, hi=None):
        func = self._make_inorder_iterator(rtype='items')
        return func(self, lo, hi)

    keys.__doc__   = _docstring.format(rtype='keys')
    values.__doc__ = _docstring.format(rtype='values')
    items.__doc__  = _docstring.format(rtype='items')

    def __iter__(self):
        """Return an iterator of all of the keys in the table."""
        yield from self.keys()

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
    def _make_inorder_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        def iterator(self, lo=None, hi=None):
            """Iterate over items with keys between `lo` and `hi`."""
            if lo is None:
                l = 0
            else:
                l = self.rank(lo)

            if hi is None:
                h = self.size
            else:
                h = self.rank(hi)
                # `hi` is included in range
                if h < self.size and self._items[h].key == hi:
                    h += 1

            q = _Queue()
            for x in self._items[l:h]:
                q.enqueue(x.key if rtype == 'keys' else
                          (x.val if rtype == 'values' else (x.key, x.val)))
            return list(q)
        return iterator

    # -------------------------------------------------------------------------
    #         Data Integrity Checks
    # -------------------------------------------------------------------------
    # Ex 3.1.30
    # NOTE integrity checks are O(N)!! They break the O(log2 N) search...
    def _assert_integrity(self):
        assert self._is_sorted() and self._rank_check()

    def _rank_check(self):
        for i in range(self.size):
            if i != self.rank(self.select(i)):
                return False
        return True

    def _is_sorted(self):
        for i in range(1, self.size):
            if self._items[i-1].key > self._items[i].key:
                return False
        return True


class BST():
    r"""Implements a binary search tree data structure.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) tuples to be put onto the tree.
    cache : bool, optional
        Cache the latest item searched.
    delete_method : str \in {'Hibbard', 'random'}
        Select method to use for deletion:
            * 'Hibbard' will replace the requested node with its successor.
            * 'random' will replace the requested node with a random choice
               between its predecessor and its successor.

    Attributes
    ----------
    size : int
        Number of items on the tree.
    height : int
        The height of the binary tree == maximum path length ~ 2.99 log2 N
    internal_path_length : int
        The sum of the depths of all nodes in the tree ~ 1.39 log2 N - 1.85
    is_empty : bool
        True if `size == 0`.
    """
    # Private Node class
    class _Node():
        """Internal node object to hold key, value, and two children."""
        def __init__(self, key, value=None):
            self.key = key
            self.val = value
            self.left = self.right = None
            self.N = 1       # nodes in subtree rooted here
            self.height = 1  # Ex 3.2.6(b) height of the tree rooted at this _Node
            self.ipl = 0     # Ex 3.2.47 sum of depths of nodes in subtree

        def __str__(self):
            # Avoid recursion through entire tree!! Just print each child
            left_str = f"{{{repr(self.left.key)}: {repr(self.left.val)}}}" if self.left else 'None'
            right_str = f"{{{repr(self.right.key)}: {repr(self.right.val)}}}" if self.right else 'None'
            return f"{{{repr(self.key)}: {repr(self.val)}}}, L:{left_str}, R:{right_str}, N={self.N}"

        def __repr__(self):
            return f"<{self.__class__.__name__}: {self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __init__(self, items=list(), cache=False, delete_method='Hibbard'):
        self._root = None
        self._CACHE_FLAG = cache       # Ex 3.2.28
        self._cache = None             # store the most recently accessed Node.
        self._cost = 0                 # Ex 3.2.39, 3.2.40, 3.2.44, 3.2.47
        self._delete_method = delete_method   # 'Hibbard' or 'random'
        try:
            for k, v in items:
                self._root = self._set(k, v, self._root)
            return
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} expects a `list` of tuples input.")

    # Add to make BST behave more like python dict
    @classmethod
    def fromkeys(cls, keys=list(), value=None):
        """Create a new BST with keys from iterable and values set to value."""
        st = cls()
        for k in keys:
            st[k] = value
        return st

    @property
    def size(self):
        return self._size(self._root)

    @property
    def height(self):
        """Return the height of the BST in O(1) time."""
        return self._height(self._root)

    @property
    def internal_path_length(self):
        """Return the internal path length of the BST in O(1) time."""
        return self._internal_path_length(self._root)

    @property
    def is_empty(self):
        return self.size == 0

    def __len__(self):
        return self.size

    def __getitem__(self, k):
        """Return the value associated with the given `k`."""
        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            return self._cache.val
        else:
            x = self._get(k, self._root)
            if self._CACHE_FLAG:
                self._cache = x
            return x.val

    def __setitem__(self, k, v):
        """Add a new node to subtree at `x`, associating `k` with `v`.
        If `k` is in subtree rooted at `x`, change its value to `v`."""
        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            self._cache.val = v
            return
        else:
            self._cost = 0  # Ex 3.2.44
            self._root = self._set(k, v, self._root)

    def __delitem__(self, k, delete_method=None):
        """Delete the node associated with `k`.

        ..note:: Implements eager Hibbard deletion.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        if delete_method is None:
            delete_method = self._delete_method

        _empty_check(self)

        if delete_method == 'Hibbard':
            self._root = self._delete(k, self._root)
        elif delete_method == 'random':
            self._root = self._delete_random(k, self._root)
        else:
            raise ValueError(f"Invalid delete_method {delete_method}!")

        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            self._cache = None

    def __contains__(self, k):
        """Return True if `k` is present in the tree, False otherwise."""
        try:
            self.__getitem__(k)
            return True
        except KeyError:
            return False

    def __eq__(self, other):
        return self.items() == sorted(other.items())

    def __str__(self):
        return str(dict(self.items()))

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Other Public Methods
    # -------------------------------------------------------------------------
    def min(self):
        """Return the minimum key in the tree.

        Raises
        ------
        KeyError
            If the table is empty.
        """
        _empty_check(self)
        return self._min(self._root).key

    def max(self):
        """Return the maximum key in the tree.

        Raises
        ------
        KeyError
            If the table is empty.
        """
        _empty_check(self)
        return self._max(self._root).key

    def floor(self, k):
        """Return the largest key less than or equal to `k`, or None if `k` is
        less than the smallest key in the table.
        """
        x = self._floor(k, self._root)  # self._floor returns a Node
        return x.key if x else None

    def ceil(self, k):
        """Return the smallest key greater than or equal to `k`, or None if `k`
        is greater than the largest key in the table.
        """
        x = self._ceil(k, self._root)  # self._ceil returns a Node
        return x.key if x else None

    def rank(self, k):
        """Return the number of keys strictly less than `k`."""
        return self._rank(k, self._root)

    def select(self, r):
        """Return the key of rank `r`.

        Raises
        ------
        IndexError
            If there are fewer than `r`+1 keys in the table.
        """
        return self._select(r, self._root).key

    def delete_min(self):
        """Delete the smallest key.

        Raises
        ------
        IndexError
            If the table is empty.
        """
        _empty_check(self)
        self._root = self._delete_min(self._root)
        if self._CACHE_FLAG:
            self._cache = None

    def delete_max(self):
        """Delete the largest key.

        Raises
        ------
        IndexError
            If the table is empty.
        """
        _empty_check(self)
        self._root = self._delete_max(self._root)
        if self._CACHE_FLAG:
            self._cache = None

    # Exercise 3.2.6(a)
    def height_r(self):
        """Determine the height of the BST recursively, in O(n) time."""
        return self._height_r(self._root)

    # Ex 3.2.47
    def internal_path_length_r(self):
        """Compute the internal path length of the tree recursively.

        ..note:: The IPL is defined as the sum of the depth of every node.
        """
        return self._internal_path_length_r(self._root, 0)

    # Exercise 3.2.25
    def is_balanced(self):
        """Return True if tree is perfectly balanced."""
        return self._is_balanced(self._root)

    def center_of_mass(self):
        """Return the left-to-right 'center of mass' of the tree.

        .. note:: negative values count nodes to the left of the root, positive
            values count nodes to the right of the root. Values of {-1, 0, 1}
            do *not* necessarily mean a balanced tree. Draw the tree with the
            input string 'AXCSERH' as an example.
        """
        _empty_check(self)
        return self._center_of_mass(self._root) / (t.size - 1)

    # Exercise 3.2.37
    def level_order(self, x=None):
        """Iterate over the keys in level-order (breadth-first)."""
        if x is None:
            x = self._root
        keys = _Queue()
        q = _Queue()
        q.enqueue(x)
        while q:
            x = q.dequeue()
            if x is None:
                continue
            keys.enqueue(x.key)
            q.enqueue(x.left)
            q.enqueue(x.right)
        return list(keys)

    # Methods to make symbol tables behave like python dict()
    def pop(self, k, *args):
        """Delete the node associated with `k`, and return its value. If the
        key is not in the table, return the given default value.

        ..note:: Implements eager Hibbard deletion.

        Raises
        ------
        KeyError
            If `k` is not in the table, and default is not given.
        """
        try:
            _empty_check(self)
            v = self.__getitem__(k)
            self._root = self._delete(k, self._root)
            if self._CACHE_FLAG and self._cache and k == self._cache.key:
                self._cache = None
            return v
        except (IndexError, KeyError) as e:
            if len(args) == 0:
                raise e
            elif len(args) == 1:
                return args[0]
            else:  # len(args) > 0
                raise TypeError(f"pop expected at most 2 arguments, got {len(args)+1}")

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
    def _size(self, x=None):
        """Return the size of the subtree rooted at Node `x`."""
        return 0 if x is None else x.N

    def _get(self, k, x=None):
        """Return the node associated with the given `k`.

        Parameters
        ----------
        k : key
            key for which to search
        x : _Node, optional
            root of the subtree at which to begin search

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        # got to the bottom of the tree, key not found
        if x is None:
            raise KeyError(k)

        if k < x.key:
            return self._get(k, x.left)
        elif k > x.key:
            return self._get(k, x.right)
        else:  # k == root.key!
            return x

    def _set(self, k, v, x=None):
        """Add a new node to subtree at `x`, associating `k` with `v`.
        If `k` is in subtree rooted at `x`, change its value to `v`.

        Parameters
        ----------
        k : key
            key for which to search
        v : value
            object to be associated with key `k`
        x : _Node, optional
            root of the subtree at which to begin search
        """
        # subtree is empty, create a new node
        if x is None:
            return self._Node(k, v)

        # create a child, or update the value
        if k < x.key:
            self._cost += 1
            x.left = self._set(k, v, x.left)
        elif k > x.key:
            self._cost += 2
            x.right = self._set(k, v, x.right)
        else:  # k == x.key
            self._cost += 2
            x.val = v  # update the value

        self._update_node(x)
        return x

    def _delete(self, k, x=None):
        """Delete the node associated with `k` using eager Hibbard deletion."""
        if x is None:
            return
        # Update links and node counts as we go vs.:
        #   t = self._get(k, self._root)
        if k < x.key:
            x.left = self._delete(k, x.left)
        elif k > x.key:
            x.right = self._delete(k, x.right)
        else:
            if x.left is None:
                return x.right
            elif x.right is None:
                return x.left
            else:
                # save pointer to Node to be deleted
                t = x
                # Get the successor to the node to be deleted
                x = self._min(t.right)
                x.right = self._delete_min(t.right)
                x.left = t.left

        self._update_node(x)
        return x

    # TODO write tests for this method
    # Idea: replace `random.random()` with `self._poss_arrow` and flip it on
    # each deletion.
    def _delete_random(self, k, x=None):
        """Delete the node associated with `k` by choosing the predecessor or
            successor at random."""
        if x is None:
            return

        if k < x.key:
            x.left = self._delete(k, x.left)
        elif k > x.key:
            x.right = self._delete(k, x.right)
        else:
            if x.left is None:
                return x.right
            elif x.right is None:
                return x.left
            else:
                # save pointer to Node to be deleted
                t = x
                if random.random() > 0.5:
                    # Get the successor to the node to be deleted
                    x = self._min(t.right)
                    x.right = self._delete_min(t.right)
                    x.left = t.left
                else:
                    # Get the predecessor to the node to be deleted
                    x = self._max(t.left)
                    x.left = self._delete_max(t.left)
                    x.right = t.right

        self._update_node(x)
        return x

    
    def _min(self, x=None):
        """Return the minimum key in the subtree rooted at `x`."""
        return x if x.left is None else self._min(x.left)

    def _max(self, x=None):
        return x if x.right is None else self._max(x.right)

    def _floor(self, k, x=None):
        """Return the Node with key that is the floor of `k`."""
        if x is None:
            return
        if k == x.key:
            return x                       # floor may be exactly k
        if k < x.key:
            return self._floor(k, x.left)  # floor must be in left subtree
        t = self._floor(k, x.right)        # floor might be in right subtree
        return t if t else x

    def _ceil(self, k, x=None):
        """Return the Node with key that is the ceiling of `k`."""
        # Note: _ceil is just _floor, interchange < <-> >, left <-> right
        if x is None:
            return
        if k == x.key:
            return x                       # ceil may be exactly k
        if k > x.key:
            return self._ceil(k, x.right)  # ceil must be in right subtree
        t = self._ceil(k, x.left)          # ceil might be in left subtree
        return t if t else x

    def _rank(self, k, x=None):
        """Return the rank of key `k` in the subtree rooted at `x`.

        .. note:: `rank` is the inverse of `select`.
        """
        if x is None:
            return 0
        if k < x.key:
            return self._rank(k, x.left)
        elif k > x.key:
            return 1 + self._size(x.left) + self._rank(k, x.right)
        else:
            return self._size(x.left)

    def _select(self, r, x=None):
        """Return the Node that has rank `r` in the subtree rooted at `x`.

        .. note:: `select` is the inverse of `rank`.

        Raises
        ------
        IndexError
            If there are fewer than `r`+1 keys in the table.
        """
        if x is None:
            raise IndexError(r)
        t = self._size(x.left)
        if t > r:
            return self._select(r, x.left)
        elif t < r:
            return self._select(r-t-1, x.right)
        else:
            return x

    def _delete_min(self, x=None):
        """Delete the minimum key in the subtree rooted at `x`.

        Returns
        -------
        x : _Node
            The root of the subtree. Will not be equal to `x` if `x` is the
            minimum key in the subtree.
        """
        if x.left is None:
            return x.right
        x.left = self._delete_min(x.left)
        self._update_node(x)
        return x

    def _delete_max(self, x=None):
        """Delete the maximum key in the subtree rooted at `x`.

        Returns
        -------
        x : _Node
            The root of the subtree. Will not be equal to `x` if `x` is the
            minimum key in the subtree.
        """
        if x.right is None:
            return x.left
        x.right = self._delete_max(x.right)
        self._update_node(x)
        return x

    def _height_r(self, x=None):
        """Return the height of the tree rooted at `x`."""
        if x is None:
            return 0
        lmax = self._height_r(x.left)
        rmax = self._height_r(x.right)
        return max(lmax, rmax) + 1

    def _height(self, x=None):
        """Return the height of the tree rooted at `x`."""
        return 0 if x is None else x.height

    def _internal_path_length_r(self, x=None, depth=0):
        """Return the sum of the depths of all nodes in the subtree."""
        if x is None:
            return 0
        lpath = self._internal_path_length_r(x.left,  depth + 1)
        rpath = self._internal_path_length_r(x.right, depth + 1)
        return depth + lpath + rpath

    def _internal_path_length(self, x=None):
        """Return the sum of the depths of all nodes in the subtree."""
        return 0 if x is None else x.ipl

    def _is_balanced(self, x=None):
        """Return True if subtree rooted at `x` is perfectly balanced."""
        if x is None:
            return True
        elif abs(self._size(x.left) - self._size(x.right)) > 1:
            return False
        else:
            return self._is_balanced(x.left) and self._is_balanced(x.right)

    def _center_of_mass(self, x=None, c=0):
        """Return the center of mass of the subtree rooted at `x`."""
        if x is None:
            return 0
        L = 0 if x.left is None else x.left.N
        R = 0 if x.right is None else x.right.N
        return (R - L
                + self._center_of_mass(x.left)
                + self._center_of_mass(x.right))

    # Convenience functions
    def _update_node(self, x):
        """Update the parameters of the node based on its subtree."""
        x.N = self._size(x.left) + self._size(x.right) + 1
        x.height = max(self._height(x.left), self._height(x.right)) + 1
        x.ipl = self._internal_path_length(x.left) + self._size(x.left) \
                + self._internal_path_length(x.right) + self._size(x.right)

    def _get_node(self, k):
        """Return the node associated with the given `k`."""
        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            return self._cache
        else:
            x = self._get(k, self._root)
            if self._CACHE_FLAG:
                self._cache = x
            return x

    # -------------------------------------------------------------------------
    #         Iterator functions
    # -------------------------------------------------------------------------
    _docstring = """Return an in-order iterator over the {rtype} between the
    keys `lo` and `hi`, inclusive. Guaranteed to be the same order as
    `BST.keys()`.

    Parameters
    ----------
    lo : key
        Minimum key over which to search, inclusive.
    hi : key
        Maximum key over which to search, inclusive.

    Returns
    -------
    q : iterator
        iterator over the {rtype} between `lo` and `hi`, inclusive.
    """

    def keys(self, lo=None, hi=None):
        func = self._make_inorder_iterator(rtype='keys')
        return func(self, lo, hi)

    def values(self, lo=None, hi=None):
        func = self._make_inorder_iterator(rtype='values')
        return func(self, lo, hi)

    def items(self, lo=None, hi=None):
        func = self._make_inorder_iterator(rtype='items')
        return func(self, lo, hi)

    keys.__doc__   = _docstring.format(rtype='keys')
    values.__doc__ = _docstring.format(rtype='values')
    items.__doc__  = _docstring.format(rtype='items')

    # factory for generic in-order iteration over keys
    def _make_inorder_iterator(self, rtype):
        """Create an iterator over the desired type."""
        def iterator(self, lo=None, hi=None):
            try:
                if lo is None:
                    lo = self.min()
                if hi is None:
                    hi = self.max()
                return self._iterate(lo, hi, x=self._root, rtype=rtype)
            except IndexError:
                return list()
        return iterator

    def _iterate(self, lo, hi, x=None, q=None, rtype='keys'):
        """Recursively range search the BST for keys between `lo` and `hi`."""
        if x is None:
            return
        if q is None:
            q = _Queue()
        # Enqueue by key order
        if lo < x.key:
            self._iterate(lo, hi, x.left, q, rtype)
        if lo <= x.key and hi >= x.key:
            q.enqueue(x.key if rtype == 'keys' else
                        (x.val if rtype == 'values' else (x.key, x.val)))
        if hi > x.key:
            self._iterate(lo, hi, x.right, q, rtype)
        return list(q)

    # iterate as a generator function
    #   * more efficient than `yield from self.keys()` for entire traversal
    #     since we don't have to find the min or max keys
    #   * also neat pythonic code!
    def __iter__(self):
        return self._iterate_keys(self._root)

    def _iterate_keys(self, x=None):
        """Recursively traverse the tree in order."""
        if x is None:
            return
        # Yield keys in order
        yield from self._iterate_keys(x.left)
        yield x.key
        yield from self._iterate_keys(x.right)

    def _iterate_nodes(self, x=None):
        """Recursively traverse the tree in order (depth-first search)."""
        if x is None:
            return
        # Yield nodes in order
        yield from self._iterate_nodes(x.left)
        yield x
        yield from self._iterate_nodes(x.right)

    # -------------------------------------------------------------------------
    #         Certification (see Exercises 3.2.29 -- 3.2.32)
    # -------------------------------------------------------------------------
    # Ex 3.2.32
    def isBST(self):
        """Assert that all of the binary search tree properties hold."""
        return self._is_binary_tree() and \
               self._is_ordered() and \
               self._has_no_duplicates()

    # Ex 3.2.29
    def _is_binary_tree(self):
        """Return True if BST is indeed binary and acyclic."""
        return self.__is_binary_tree(self._root)

    def __is_binary_tree(self, x=None):
        """Return True if the subtree count field `N` is consistent in the data
        structure rooted at Node `x`.
        """
        if x is None:
            return True
        elif self._size(x) != 1 + self._size(x.left) + self._size(x.right):
            return False
        else:
            return self.__is_binary_tree(x.left) and \
                   self.__is_binary_tree(x.right)

    # Ex 3.2.30
    def _is_ordered(self):
        """Return True if all keys in the tree are in order."""
        return self.__is_ordered(lo=self.min(), hi=self.max(), x=self._root)

    def __is_ordered(self, lo=None, hi=None, x=None):
        """Return True if all keys in the tree are between the `min` and `max`
        values in the tree, and the BST ordering property holds for all keys.
        """
        if x is None:
            return True
        elif (lo is not None and self._min(x).key < lo) or \
             (hi is not None and self._max(x).key > hi):
            return False
        else:
            return self.__is_ordered(lo, x.key, x.left) and \
                   self.__is_ordered(x.key, hi, x.right)

    # Ex 3.2.31
    def _has_no_duplicates(self):
        """Return True if there are no equal keys in the BST."""
        for i, k in enumerate(self.keys()):
            if i > 0 and p > k:
                return False
            p = k  # track previously seen key
        return True


# Exercise 3.2.34 extended API
class ThreadedST(BST):
    """Implements an extended binary search tree data structure, where the
    nodes contain pointers to their successor and predecessor.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) tuples to be put onto the tree.

    Attributes
    ----------
    size : int
        Number of items on the tree.
    height : int
        The height of the binary tree == maximum path length ~ log2 N
    is_empty : bool
        True if `size == 0`.
    """
    # Add predecessor and successor nodes
    class _Node(BST._Node):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.next = None  # in-order successor
            self.prev = None  # in-order predecessor

    def next(self, k):
        """Return the key that follows `k`, None if `k` is the maximum."""
        x = self._get(k, self._root).next
        return x.key if x else None

    def prev(self, k):
        """Return the key that precedes `k`, None if `k` is the minimum."""
        x = self._get(k, self._root).prev
        return x.key if x else None

    def print_threads(self):
        """Print the next/prev nodes for each key in the tree."""
        print("k  {:40}    {:40}".format('prev', 'next'))
        for k in self.keys():
            print("{}: {:40} || {:40}"
                    .format(k, str(self._get(k, self._root).prev),
                               str(self._get(k, self._root).next)))

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
    def _set(self, k, v, x=None):
        """Add a new node to subtree at `x`, associating `k` with `v`.
        If `k` is in subtree rooted at `x`, change its value to `v`.

        Parameters
        ----------
        k : key
            key for which to search
        v : value
            object to be associated with key `k`
        x : _Node, optional
            root of the subtree at which to begin search
        """
        # subtree is empty, create a new node
        if x is None:
            return self._Node(k, v)

        # create a child, or update the value
        if k < x.key:
            x.left = self._set(k, v, x.left)
            x.left.next = self._find_next(x.left.key, self._root)
            x.left.prev = self._find_prev(x.left.key, self._root)
        elif k > x.key:
            x.right = self._set(k, v, x.right)
            x.right.next = self._find_next(x.right.key, self._root)
            x.right.prev = self._find_prev(x.right.key, self._root)
        else:  # k == x.key
            x.val = v  # update the value

        # Update the size of the subtree located at the given root
        self._update_node(x)
        x.next = self._find_next(x.key, self._root)
        x.prev = self._find_prev(x.key, self._root)
        return x

    def _delete(self, k, x=None):
        """Delete the node associated with `k`.

        ..note:: Implements eager Hibbard deletion.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        if x is None:
            return
        if k < x.key:
            x.left = self._delete(k, x.left)
        elif k > x.key:
            x.right = self._delete(k, x.right)
        else:
            if x.left is None:
                # Update threads
                if x.next:
                    x.next.prev = x.prev
                if x.prev:
                    x.prev.next = x.next
                return x.right
            elif x.right is None:
                # Update threads
                if x.next:
                    x.next.prev = x.prev
                if x.prev:
                    x.prev.next = x.next
                return x.left
            else:
                # save pointer to Node to be deleted
                t = x
                # Get the successor to the node to be deleted
                x = self._min(t.right)
                x.right = self._delete_min(t.right)
                x.left = t.left
                # Update Threads: _delete_min frees x, so reattach it
                x.next = t.next
                x.prev = t.prev
                if t.next:
                    t.next.prev = x
                if t.prev:
                    t.prev.next = x

        self._update_node(x)  # update N, height, internal path length
        return x

    def _delete_min(self, x=None):
        """Delete the smallest key from the subtree rooted at `x`.

        Returns
        -------
        r : _Node
            The root of the subtree. Will not be equal to `x` if `x` is the
            minimum key in the subtree.
        """
        if x.left is None:
            # Update threads
            if x.next:
                x.next.prev = x.prev
            if x.prev:
                x.prev.next = x.next
            return x.right
        x.left = self._delete_min(x.left)
        self._update_node(x)  # update N, height, internal path length
        return x

    def _delete_max(self, x=None):
        """Delete the largest key from the subtree rooted at `x`.

        Returns
        -------
        r : _Node
            The root of the subtree. Will not be equal to `x` if `x` is the
            minimum key in the subtree.
        """
        if x.right is None:
            # Update threads
            if x.next:
                x.next.prev = x.prev
            if x.prev:
                x.prev.next = x.next
            return x.left
        x.right = self._delete_max(x.right)
        self._update_node(x)  # update N, height, internal path length
        return x

    def _find_next(self, k, x=None, s=None):
        """Return the Node that follows `k`, None if `k` is the maximum.

        Parameters
        ----------
        k : key
            key for which to find the successor Node
        x : _Node, optional
            root of the subtree at which to begin search
        s : _Node, optional
            pointer to successor of Node `k`. Used for recursion only.

        Returns
        -------
        s : _Node
            in-order successor of Node `k`.
        """
        if x is None:
            return None
        if k < x.key:
            return self._find_next(k, x.left, x)  # update successor pointer
        elif k == x.key:
            if x.right:
                return self._min(x.right)  # successor is min of right subtree
            else:
                return s
        else:  # k > x.key:
            return self._find_next(k, x.right, s)

    def _find_prev(self, k, x=None, s=None):
        """Return the Node that precedes `k`, None if `k` is the minimum.

        Parameters
        ----------
        k : key
            key for which to find the successor Node
        x : _Node, optional
            root of the subtree at which to begin search
        s : _Node, optional
            pointer to successor of Node `k`. Used for recursion only.

        Returns
        -------
        s : _Node
            in-order successor of Node `k`.
        """
        if x is None:
            return None
        if k < x.key:
            return self._find_prev(k, x.left, s)
        elif k == x.key:
            if x.left:
                return self._max(x.left)  # predecessor is max of left subtree
            else:
                return s
        else:  # k > x.key
            return self._find_prev(k, x.right, x)  # update predecessor pointer


class BST_nr(BST):
    """Implements a binary search tree data structure, non-recursively.

    ..note:: `BST_nr` subclasses `BST`, but only overrides the internal methods
    for `_set`, `_get`, `_delete`, etc. 

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) tuples to be put onto the tree.

    Attributes
    ----------
    size : int
        Number of items on the tree.
    height : int
        The height of the binary tree == maximum path length ~ log2 N
    internal_path_length : int
        The sum of the depths of all nodes in the tree ~ 1.39 log2 N - 1.85
    is_empty : bool
        True if `size == 0`.
    """
    # -------------------------------------------------------------------------
    #         Implement get, set, delete non-recursively
    # -------------------------------------------------------------------------
    def _get(self, k, x):
        """Return the Node associated with the given key `k` in the subtree
        rooted at `x`.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        while x:
            if k == x.key:
                if self._CACHE_FLAG:
                    self._cache = x
                return x
            elif k < x.key:
                x = x.left
            else:
                x = x.right
        else:
            raise KeyError(k)

    def _set(self, k, v, x):
        """Add a new node to subtree at `x`, associating `k` with `v`.
        If `k` is in subtree rooted at `x`, change its value to `v`.

        ..note:: in the non-recursive implementation, `x` will always be
            `self._root`, as called from the BST parent class.
        """
        s = _Stack()  # track all nodes on path for updates
        p = self._root
        while x:
            p = x  # track parent node
            if k == x.key:
                x.val = v  # update the value if found
                if self._CACHE_FLAG:
                    self._cache = x
                return self._root
            else:
                # Move down the tree
                s.push(x)
                if k < x.key:
                    self._cost += 1
                    x = x.left
                else:
                    self._cost += 2
                    x = x.right

        # Insert new node as child of parent
        if p is None:
            self._root = self._Node(k, v)
            cache = self._root
        elif k < p.key:
            p.left = self._Node(k, v)
            cache = p.left
        else:
            p.right = self._Node(k, v)
            cache = p.right

        if self._CACHE_FLAG:
            self._cache = cache

        # Update node counts and heights on path traveled back up the tree
        while s:
            x = s.pop()
            self._update_node(x)  # update N, height, internal path length

        return self._root

    def _delete(self, k, t):
        """Delete the node associated with `k`.

        ..note:: Implements eager Hibbard deletion.
        ..note:: in the non-recursive implementation, `t` will always be
            `self._root`, as called from the BST parent class.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        s = _Stack()  # stack of visited nodes to update counts

        # find node to delete
        p = t
        while t:
            if k == t.key:
                if self._CACHE_FLAG and self._cache and k == self._cache.key:
                    self._cache = None
                break
            else:
                # Move down the tree
                s.push(t)
                p = t  # keep pointer to parent
                if k < t.key:
                    t = t.left
                else:
                    t = t.right
        else:
            raise KeyError(k)

        # find its successor
        if t.left is None:
            x = t.right
        elif t.right is None:
            x = t.left
        else:
            x = self._min(t.right)
            s.push(x)
            x.right = self._delete_min(t.right)
            x.left = t.left

        # Update parent link
        if k == p.key:
            self._root = x
        elif k < p.key:
            p.left = x
        else:
            p.right = x

        # Update node counts from successor back up the tree
        #   (_delete_min operation updates the counts in the right subtree)
        while s:
            t = s.pop()
            self._update_node(t)  # update N, height, internal path length

        return self._root

    # -------------------------------------------------------------------------
    #         Other Private Methods
    # -------------------------------------------------------------------------
    def _min(self, x):
        """Return the node with the minimum key in the subtree rooted at `x`."""
        while x.left:
            x = x.left
        return x

    def _max(self, x):
        """Return the node with the maximum key in the subtree rooted at `x`."""
        while x.right:
            x = x.right
        return x

    def _floor(self, k, x):
        """Return the Node corresponding to the largest key less than or equal
        to `k` in the subtree rooted at `x`, or None if `k` is less than the
        smallest key in the table.
        """
        p = None  # pointer to the floor Node
        while x:
            if k == x.key:
                p = x
                break
            elif k < x.key:
                x = x.left  # floor must be in left subtree
            else:
                p = x       # keep pointer to parent
                x = x.right
        return p

    def _ceil(self, k, x):
        """Return the Node corresponding to the smallest key greater than or
        equal to `k` in the subtree rooted at `x`, or None if `k` is greater
        than the largest key in the table.
        """
        p = None  # pointer to the floor Node
        while x:
            if k == x.key:
                p = x
                break
            elif k > x.key:
                x = x.right  # ceil must be in right subtree
            else:
                p = x        # keep pointer to parent
                x = x.left
        return p

    def _rank(self, k, x):
        """Return the number of keys less than `k` in the subtree rooted at `x`.

        .. note:: `rank` is the inverse of `select`.
        """
        r = 0
        while x:
            if k == x.key:
                r += self._size(x.left)      # count all left of this node
                break
            elif k < x.key:
                x = x.left                   # no change to the count
            else:
                r += 1 + self._size(x.left)  # count this node + all left of it
                x = x.right
        return r

    def _select(self, r, x):
        """Return the Node corresponding to the key of rank `r` in the subtree
        rooted at `x`.

        .. note:: `select` is the inverse of `rank`.

        Raises
        ------
        IndexError
            If there are fewer than `r`+1 keys in the table.
        """
        rank = r  # track desired rank
        while x:
            t = self._size(x.left)
            if t == rank:           # found the right number!
                return x
            elif t > rank:          # there are more nodes left than we want
                x = x.left
            else:                   # there are fewer nodes left than we want
                rank -= (t + 1)     # reset desired rank in new subtree
                x = x.right
        else:
            raise IndexError(r)

    def _delete_min(self, x=None):
        """Delete the smallest key from the subtree rooted at `x`.

        Returns
        -------
        r : _Node
            The root of the subtree. Will not be equal to `x` if `x` is the
            minimum key in the subtree.
        """
        if x is None:
            x = self._root
        if x.left is None:  # the min is the root
            return x.right
        else:
            # find the min
            r = x  # keep pointer to the root
            while x.left:
                p = x         # pointer to the parent
                p.N -= 1      # decrement node counts
                x = x.left
            p.left = x.right  # delete the pointer to the min
            self._update_node(p)
            return r

    def _delete_max(self, x=None):
        """Delete the smallest key from the subtree rooted at `x`.

        Returns
        -------
        r : _Node
            The root of the subtree. Will not be equal to `x` if `x` is the
            minimum key in the subtree.
        """
        if x is None:
            x = self._root
        if x.right is None:  # the max is the root
            return x.left
        else:
            # find the max
            r = x
            while x.right:
                p = x         # pointer to the parent
                p.N -= 1      # decrement node counts
                x = x.right
            p.right = x.left  # delete the pointer to it
            self._update_node(p)
            return r

    # -------------------------------------------------------------------------
    #         Iterator
    # -------------------------------------------------------------------------
    # Exercise 3.2.36
    def _iterate(self, lo, hi, rtype='keys', **kwargs):
        """Add items to a Queue, in key-order from `lo` to `hi`."""
        q = _Queue()    # the output queue
        s = _Stack()    # visited nodes so we can pop back up the tree
        x = self._root
        while s or x:
            # Move left until `lo` is found
            if x is not None and lo < x.key:
                s.push(x)
                x = x.left
            else:
                if x is None:
                    x = s.pop()
                if lo <= x.key and hi >= x.key:
                    q.enqueue(x.key if rtype == 'keys' else
                              (x.val if rtype == 'values' else (x.key, x.val)))
                # Move right until `hi` is found
                if hi > x.key:
                    x = x.right
                else:
                    break
        return list(q)

    # Overwrite BST._iterate_keys recursive call
    def __iter__(self):
        yield from self.keys()


# Exercise 3.2.34 extended API
class ThreadedST_nr(BST_nr):
    """Implements an extended binary search tree data structure, where the
    nodes contain pointers to their successor and predecessor.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) tuples to be put onto the tree.

    Attributes
    ----------
    size : int
        Number of items on the tree.
    height : int
        The height of the binary tree == maximum path length ~ log2 N
    is_empty : bool
        True if `size == 0`.
    """
    # Re-use classes/methods from ThreadedST, but do *not* sub-class so we
    # retain non-recursive methods from BST_nr.
    _Node = ThreadedST._Node
    next = ThreadedST.next
    prev = ThreadedST.prev
    print_threads = ThreadedST.print_threads

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
    def _set(self, k, v, x):
        """Add a new node to subtree at `x`, associating `k` with `v`.
        If `k` is in subtree rooted at `x`, change its value to `v`.

        ..note:: in the non-recursive implementation, `x` will always be
            `self._root`, as called from the BST parent class.
        """
        s = _Stack()  # track all nodes on path for updates
        p = self._root
        while x:
            p = x  # track parent node
            if k == x.key:
                x.val = v  # update the value if found
                return self._root
            else:
                # Move down the tree
                s.push(x)
                if k < x.key:
                    x = x.left
                else:
                    x = x.right

        # Insert new node as child of parent
        if p is None:
            self._root = self._Node(k, v)
            return self._root
        elif k < p.key:
            p.left = self._Node(k, v)
            x = p.left
        else:
            p.right = self._Node(k, v)
            x = p.right

        # Initialize next/prev pointers of newly added node
        x.next = self._find_next(x.key)
        x.prev = self._find_prev(x.key)

        # Update node counts and heights on path traveled back up the tree
        while s:
            x = s.pop()
            self._update_node(x)
            x.next = self._find_next(x.key)
            x.prev = self._find_prev(x.key)

        return self._root

    def _delete(self, k, t):
        """Delete the node associated with `k`.

        ..note:: Implements eager Hibbard deletion.
        ..note:: in the non-recursive implementation, `t` will always be
            `self._root`, as called from the BST parent class.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        s = _Stack()  # stack of visited nodes to update counts

        # find node to delete
        p = t
        while t:
            if k == t.key:
                break
            else:
                # Move down the tree
                s.push(t)
                p = t  # keep pointer to parent
                if k < t.key:
                    t = t.left
                else:
                    t = t.right
        else:
            raise KeyError(k)

        # find its successor
        has_two_children = False
        if t.left is None:
            x = t.right
        elif t.right is None:
            x = t.left
        else:
            has_two_children = True
            x = self._min(t.right)
            s.push(x)
            x.right = self._delete_min(t.right)
            x.left = t.left

        # Update threads
        if not has_two_children:
            # No need to touch x, may not be successor
            if t.next:
                t.next.prev = t.prev
            if t.prev:
                t.prev.next = t.next
        else:
            # _delete_min frees x, so reattach it
            x.next = t.next
            x.prev = t.prev
            if t.next:
                t.next.prev = x
            if t.prev:
                t.prev.next = x

        # Update parent link
        if k == p.key:
            self._root = x
        elif k < p.key:
            p.left = x
        else:
            p.right = x

        # Update node counts from successor back up the tree
        #   (_delete_min operation updates the counts in the right subtree)
        while s:
            t = s.pop()
            self._update_node(t)

        return self._root

    def _delete_min(self, x=None):
        """Delete the smallest key from the subtree rooted at `x`.

        Returns
        -------
        r : _Node
            The root of the subtree. Will not be equal to `x` if `x` is the
            minimum key in the subtree.
        """
        if x is None:
            x = self._root
        if x.left is None:  # the min is the root
            r = x.right
        else:
            # find the min
            r = x  # keep pointer to the root
            while x.left:
                p = x           # pointer to the parent
                p.N -= 1        # decrement node counts
                x = x.left
            p.left = x.right    # delete the pointer to the min
            self._update_node(p)
        # Update threads
        if x.next:
            x.next.prev = x.prev
        if x.prev:
            x.prev.next = x.next
        return r

    def _delete_max(self, x=None):
        """Delete the largest key from the subtree rooted at `x`.

        Returns
        -------
        r : _Node
            The root of the subtree. Will not be equal to `x` if `x` is the
            minimum key in the subtree.
        """
        if x is None:
            x = self._root
        if x.right is None:  # the max is the root
            r = x.left
        else:
            # find the max
            r = x  # keep pointer to the root
            while x.right:
                p = x               # pointer to the parent
                p.N -= 1            # decrement node counts
                x = x.right
            p.right = x.left        # delete the pointer to it
            self._update_node(p)
        # Update threads
        if x.next:
            x.next.prev = x.prev
        if x.prev:
            x.prev.next = x.next
        return r

    def _find_next(self, k):
        """Return the Node that follows `k`, None if `k` is the maximum."""
        s = _Stack()  # track all nodes on path for updates
        x = p = self._root
        while x:
            p = x  # track parent node
            if k == x.key:
                break
            else:
                # Move down the tree
                s.push(x)
                if k < x.key:
                    x = x.left
                else:
                    x = x.right

        # `p` is the node to be updated
        if p.right:
            return self._min(p.right)
        else:
            # search for maximum parent node
            while s:
                x = s.pop()
                if x.key > p.key:
                    return x

    def _find_prev(self, k):
        """Return the Node that precedes `k`, None if `k` is the minimum."""
        s = _Stack()  # track all nodes on path for updates
        x = p = self._root
        while x:
            p = x  # track parent node
            if k == x.key:
                break
            else:
                # Move down the tree
                s.push(x)
                if k < x.key:
                    x = x.left
                else:
                    x = x.right

        # `p` is the node to be updated
        if p.left:
            return self._max(p.left)
        else:
            # search for minimum parent node
            while s:
                x = s.pop()
                if x.key < p.key:
                    return x

    # -------------------------------------------------------------------------
    #         Iterator
    # -------------------------------------------------------------------------
    def _iterate(self, lo, hi, rtype='keys', **kwargs):
        """Add items to a Queue, in key-order from `lo` to `hi`."""
        q = _Queue()               # the output queue
        x = self._min(self._root)  # get the minimum Node
        while x:
            if lo > x.key:
                x = x.next
            else:
                if lo <= x.key and hi >= x.key:
                    q.enqueue(x.key if rtype == 'keys' else
                                (x.val if rtype == 'values' else (x.key, x.val)))
                    x = x.next
                else:
                    break
        return list(q)

# Ex  3.2.41 array representation
# class ArrayBST(BST):
#     """Implements a binary search tree represented by parallel arrays."""


# -----------------------------------------------------------------------------
#         Test Functions
# -----------------------------------------------------------------------------
# TODO move to proper unit testing script
# Ex 3.1.29 (and then some!)
if __name__ == '__main__':
    import numpy as np
    rng = np.random.default_rng(seed=565656)

    # Define test counts
    tests = fails = 0

    def should_be(a, b, name=None, verbose=False):
        """Test a condition."""
        global tests, fails
        tests += 1
        try:
            assert a == b
            if verbose:
                print(f"[{name}]: Got: {a}, Expected: {b}")
        except AssertionError as e:
            fails += 1
            print(f"[{name}]: Got: {a}, Expected: {b}")
            raise e

    def err_test(container, op, *args, err_type=IndexError):
        """Test for raising a given error type.

        Parameters
        ----------
        container : list-like container data type instance
            A class instance to be tested.
        op : str
            attribute name of method to test
        *args : list
            arguments to `op`.
        err_type : Exception, optional
            error type that object is expected to raise

        Raises
        ------
        Exception
            If error raised is not of type `err_type`.
        """
        global tests, fails
        tests += 1
        try:
            getattr(container, op)(*args)  # call the method
        except err_type:
            return
        except Exception as err:
            fails += 1
            print(f"Raised: {repr(err)}, Expected: {err_type}")
            raise err
        else:
            fails += 1
            print(f"No error raised! Expected: {err_type}")
            raise

    # Prepare test data
    test_str = 'SEARCHEXAMPLE'
    test_set = set(test_str)
    data = [(c, i) for i, c in enumerate(test_str)]
    data_set = data.copy()
    data_set.remove(('E', 1))
    data_set.remove(('A', 2))
    data_set.remove(('E', 6))

    # ---------- Test All STs ----------
    for ST in [SequentialSearchST, ArrayST, BinarySearchST, BST, #BST_nr, 
               ThreadedST, ThreadedST_nr]:
        st = ST()
        should_be(st.size, 0)
        should_be(st.is_empty, True)
        should_be(st.keys(),   [])
        should_be(st.values(), [])
        should_be(st.items(),  [])

        st = ST(data)
        for k, v in data:
            should_be(k in st, True)
            if k == 'E' or k == 'A':
                should_be(st[k], max([val for key, val in data if key == k]))
            else:
                should_be(st[k], v)

        should_be(len(st), len(test_set))  # test __len__
        should_be(len(st), st.size)
        # st.keys() not guaranteed in order, so these tests are weak
        should_be(sorted(st.keys()), sorted(test_set))
        should_be(sorted(st.values()), sorted([v for k, v in data_set]))
        should_be(sorted(st.items()), sorted(data_set))

        err_test(st, '__getitem__', 'Z', err_type=KeyError)

        test_keys = test_set.copy()
        for k in st:
            v = st[k]
            del st[k]
            test_keys -= set(k)
            should_be(sorted(st.keys()), sorted(test_keys))

        # Test caching
        st = ST(data, cache=True)
        for k in st:
            v = st[k]                       # __getitem__
            should_be(st._cache.key, k)
            should_be(st._cache.val, v)
            st[k] = 56                       # __setitem__
            should_be(st._cache.key, k)
            should_be(st._cache.val, 56)
        del st[k]
        should_be(st._cache, None)

    # Test self-organizing search (Exercise 3.1.22)
    st = ArrayST(data, selforg=True)
    rand_keys = rng.choice(st.keys(), size=st.size)
    for k in rand_keys:
        st[k]                       # search for the key
        should_be(st.keys()[0], k)  # should get moved to front
        st[k]                       # search again
        should_be(st._cost, 1)      # test cost

    # Test self-organizing search AND caching
    st = ArrayST(data, selforg=True, cache=True)
    rand_keys = rng.choice(st.keys(), size=st.size)
    for k in rand_keys:
        st[k]                       # search for the key
        should_be(st.keys()[0], k)  # should get moved to front
        should_be(st._cache.key, k)
    del st[k]
    should_be(st._cache, None)

    # ---------- Test Ordered Operations ----------
    for ST in [BinarySearchST, BST, BST_nr, ThreadedST, ThreadedST_nr]:
        for cache in [False, True]:
            t = ST()
            # Test bad input type
            err_test(t, '__init__', list('BADEXAMPLE'), err_type=ValueError)
            # Test empty table operations
            should_be(t.size, 0)
            should_be(t.is_empty, True)
            should_be(t.keys(),   [])
            should_be(t.values(), [])
            should_be(t.items(),  [])
            err_test(t, '__getitem__', 'A', err_type=KeyError)
            err_test(t, 'min', err_type=IndexError)
            err_test(t, 'max', err_type=IndexError)
            err_test(t, 'delete_min', err_type=IndexError)
            err_test(t, 'delete_max', err_type=IndexError)
            should_be(t.floor('A'),  None)
            should_be(t.ceil('A'),  None)
            should_be(t.rank('A'),  0)
            err_test(t, 'select', 0, err_type=IndexError)

            # Test insert/get single node
            t['A'] = 0
            should_be(t['A'], 0)

            # Test construction by list of tuples
            t = ST(data, cache=cache)

            if isinstance(t, BinarySearchST):
                should_be(t._assert_integrity(), None)

            # Binary Search Tree:
            #  height depth
            #  6      0           S
            #                    / \
            #  5      1         E   X
            #                /    \
            #  4      2     A      R
            #                \    /
            #  3      3       C  H
            #                     \
            #  2      4            M
            #                     / \
            #  1      5          L   P

            should_be(len(t), len(test_set))  # test __len__
            should_be(len(t), t.size)

            for k, v in data:
                # test __contains__
                should_be(k in t, True)

                # test __getitem__
                if k == 'E' or k == 'A':
                    should_be(t[k], max([v for key, v in data if key == k]))
                else:
                    should_be(t[k], v)

            # Test __contains__ for item *not* in table
            should_be('B' in t, False)

            should_be(t.min(), 'A')
            should_be(t.max(), 'X')

            should_be(t.floor('H'), 'H')  # key in table
            should_be(t.ceil('H'),  'H')
            should_be(t.floor('Q'), 'P')  # key not in table
            should_be(t.ceil('Q'),  'R')
            should_be(t.floor(chr(ord('A') - 1)), None)  # char < t.min()
            should_be(t.ceil('Z'), None)                 # char > t.max()

            # Select and Rank tests
            err_test(t, 'select', -1, err_type=IndexError)  # too small
            for i, c in enumerate(sorted(test_set)):
                should_be(t.select(i), c)
                should_be(t.rank(c), i)
            err_test(t, 'select', 99, err_type=IndexError)  # too large

            # Ex 3.2.33
            for i in range(t.size):
                should_be(t.rank(t.select(i)), i)

            for k in t.keys():
                should_be(t.select(t.rank(k)), k)

            # BST-specific tests
            if isinstance(t, BST):
                should_be(t.height_r(), 6)  # recursive method
                should_be(t.height, 6)      # Node attribute method, as a property
                should_be(t.isBST(), True)
                should_be(list(t.level_order()), list('SEXARCHMLP'))
                should_be(t.internal_path_length_r(), 26)
                should_be(t.internal_path_length, 26)
                del t['H']  # remove node with single child
                should_be(t.height_r(), 5)  # recursive method
                should_be(t.height, 5)      # Node attribute method, as a property
                should_be(t.internal_path_length, 20)
                t = ST(data, cache=cache)
                t['G'] = 6
                should_be(t.internal_path_length, 30)
                del t['H']  # remove node with two children
                should_be(t.internal_path_length, 25)

            # In-order traversal
            t = ST(data, cache=cache)
            should_be(list(t.keys()), sorted(test_set))
            should_be(list(t.keys(lo='P')), list('PRSX'))
            should_be(list(t.keys('F', 'Q')), list('HLMP'))  # subset of keys
            should_be(list(t.keys(hi='P')), list('ACEHLMP'))

            should_be(list(t.values()), [v for k, v in sorted(data_set)])
            should_be(list(t.items()), sorted(data_set))

            # Test deletion and reinsertion
            k, v = t.min(), t[t.min()]
            t.delete_min()  # remove 'A'
            should_be(t.min(), 'C')
            # Test updated ranks
            for i, c in enumerate(sorted(test_set - set(k))):
                should_be(t.select(i), c)
                should_be(t.rank(c), i)
            t[k] = v  # replace value

            k, v = t.max(), t[t.max()]
            t.delete_max()  # remove 'X'
            should_be(t.max(), 'S')
            # Test updated ranks
            for i, c in enumerate(sorted(test_set - set(k))):
                should_be(t.select(i), c)
                should_be(t.rank(c), i)
            t[k] = v  # replace value

            # Delete arbitrary key, starting with same tree
            for k in test_set:
                t = ST(data)
                v = t[k]
                del t[k]
                should_be(len(t), len(test_set)-1)
                err_test(t, '__getitem__', k, err_type=KeyError)

            if isinstance(t, BST):
                t = ST(data)  # reset tree
                # delete the root
                should_be(t._root.key, 'S')
                v = t['S']
                del t['S']
                should_be(len(t), len(test_set)-1)
                should_be(t._root.key, 'X')
                t['S'] = v

    # Test comparisons between objects (in *both* directions)
    should_be(SequentialSearchST(data), BinarySearchST(data))
    should_be(BinarySearchST(data), SequentialSearchST(data))
    should_be(BinarySearchST(data), BST(data))
    should_be(BST(data), BinarySearchST(data))
    should_be(BST(data), BST_nr(data))
    should_be(BST_nr(data), BST(data))

    # -------------------------------------------------------------------------
    #         Test ThreadedST methods
    # -------------------------------------------------------------------------
    def test_threads(t, test_set):
        """Test that the next/prev attributes are set properly."""
        keys = sorted(test_set)
        for i, k in enumerate(keys[:-1]):
            should_be(t.next(k), keys[i+1])
        should_be(t.next(keys[-1]), None)

        keys = sorted(test_set, reverse=True)
        for i, k in enumerate(keys[:-1]):
            should_be(t.prev(k), keys[i+1])
        should_be(t.prev(keys[-1]), None)

    for ST in [ThreadedST, ThreadedST_nr]:
        t = ST(data)
        test_threads(t, test_set)

        k, v = t.min(), t[t.min()]
        t.delete_min()  # remove 'A'
        test_threads(t, sorted(test_set - set(k)))
        t[k] = v

        k, v = t.max(), t[t.max()]
        t.delete_max()  # remove 'X'
        test_threads(t, sorted(test_set - set(k)))
        t[k] = v

        # Delete arbitrary key, starting with same tree
        for k in test_set:
            t = ST(data)
            v = t[k]
            del t[k]
            test_threads(t, sorted(test_set - set(k)))

    # Summary
    if fails > 0:
        print(f"{fails}/{tests} tests failed")
    else:
        print(f"All {tests} tests passed!")

# =============================================================================
# =============================================================================
