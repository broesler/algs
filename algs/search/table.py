#!/usr/bin/env python3
# =============================================================================
#     File: basics.py
#  Created: 2021-03-02 09:57
#   Author: Bernie Roesler
#
"""
  Description: Elementary Symbol Tables
"""
# =============================================================================

from abc import ABC, abstractmethod

from algs.basics import Queue
from algs.sort import mergesort

__all__ = ['SequentialSearchST', 'BinarySearchST', 'ArrayST']


# -----------------------------------------------------------------------------
#         Define Abstract Base Classes
# -----------------------------------------------------------------------------
class SymbolTable(ABC):
    # An abstract base class implementing an unordered symbol table.
    # NOTE `SymbolTable` lacks methods like `min`/`max`,
    # `floor`/`ceil`, etc. that the ordered symbol tables (`BinarySearchST`,
    # BST, etc.) can efficiently implement.

    # Define doc parts separately for subclasses to augment.
    _attribs_doc = """
    Attributes
    ----------
    size : int
        Number of items in the table.
    is_empty : bool
        True if `size == 0`."""

    _other_doc = """
    Raises
    ------
    KeyError
        If `k` is not in the table, or if the table is empty.
    """

    __doc__ = _attribs_doc + "\n" + _other_doc

    def __init__(self, items=None, cache=False):
        """
        Parameters
        ----------
        items : mapping, dict-like, optional
            Iterable of (key, value) pairs to be put into the table.
        cache : bool, optional
            If True, cache the most recent search result.
        """
        self._cost = 0            # cost of previous get/put/delete
        self._CACHE_FLAG = cache  # to cache or not to cache
        self._cache = None        # store latest search hit
        # Initialize the symbol table
        items = items or []
        try:
            for k, v in items:
                self.__setitem__(k, v)
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             'expects an iterable mapping input.')

    # Additional constructor
    @classmethod
    def fromkeys(cls, keys=None, value=None, **kwargs):
        """Create a new BST with keys from iterable and values set to value."""
        keys = [] if keys is None else keys
        st = cls(**kwargs)
        for k in keys:
            st[k] = value
        return st

    @property
    @abstractmethod
    def size(self):
        """Number of elements in the table."""
        pass

    @property
    def is_empty(self):
        return self.size == 0

    def _empty_check(self):
        """General assertion that table is not empty."""
        if self.is_empty:
            raise KeyError(f"{self.__class__.__name__} is empty!")

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
        if len(self) < 30:
            return str(self.items())
        else:
            a = self.items()
            return str(a[:10]) + ' ... ' + str(a[-10:])

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Core methods
    # -------------------------------------------------------------------------
    # Aliased methods to match with Algorithms book API
    def put(self, k, v):
        return self.__setitem__(k, v)

    def get(self, k):
        return self.__getitem__(k)

    def delete(self, k):
        return self.__delitem__(k)

    @abstractmethod
    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`."""
        pass

    @abstractmethod
    def __getitem__(self, k, v):
        """Return the value associated with the given key `k`."""
        pass

    @abstractmethod
    def __delitem__(self, k):
        """Delete the item associated with `k`."""
        pass

    # -------------------------------------------------------------------------
    #         Iterator functions
    # -------------------------------------------------------------------------
    def __iter__(self):
        """Return an iterator of all of the keys in the table.

        Yields
        ------
        keys : iterable of keys
        """
        yield from self.keys()

    _docstring = """Return a list of the {rtype}`.

    Returns
    -------
    q : list
        list of the {rtype}.
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

    def _make_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        return NotImplemented


class OrderedSymbolTable(SymbolTable):
    # An abstract base class implementing an ordered symbol table.
    @abstractmethod
    def min(self):
        """Return the minimum key in the table."""
        pass

    @abstractmethod
    def max(self):
        """Return the maximum key in the table."""
        pass

    @abstractmethod
    def floor(self, k):
        """Return the largest key less than or equal to `k`, or None if `k` is
        less than the smallest key in the table.
        """
        pass

    @abstractmethod
    def ceil(self, k):
        """Return the smallest key greater than or equal to `k`, or None if `k`
        is greater than the largest key in the table.
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
            If there are fewer than `r`+1 keys in the table.
        """
        pass

    @abstractmethod
    def delete_min(self):
        """Delete the minimum key in the table."""
        pass

    @abstractmethod
    def delete_max(self):
        """Delete the maximum key in the table."""
        pass

    # -------------------------------------------------------------------------
    #         Ordered Iteration
    # -------------------------------------------------------------------------
    _docstring = """Return an in-order list of the {rtype} between the keys
    `lo` and `hi`, inclusive. Guaranteed to be the same order as `ST.keys()`.

    Parameters
    ----------
    lo : key
        Minimum key over which to search, inclusive.
    hi : key
        Maximum key over which to search, inclusive.

    Returns
    -------
    q : list
        list of the {rtype} between `lo` and `hi`, inclusive.
    """

    def keys(self, lo=None, hi=None):
        func = self._make_range_iterator(rtype='keys')
        return func(self, lo, hi)

    def values(self, lo=None, hi=None):
        func = self._make_range_iterator(rtype='values')
        return func(self, lo, hi)

    def items(self, lo=None, hi=None):
        func = self._make_range_iterator(rtype='items')
        return func(self, lo, hi)

    keys.__doc__   = _docstring.format(rtype='keys')
    values.__doc__ = _docstring.format(rtype='values')
    items.__doc__  = _docstring.format(rtype='items')

    def _make_range_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        return NotImplemented


# -----------------------------------------------------------------------------
#         Concrete Classes
# -----------------------------------------------------------------------------
# Private class of key/value pairs
class _Item():
    """Internal item object to hold key and value."""
    def __init__(self, key, value):
        self.key = key
        self.val = value

    def __str__(self):
        return f"({repr(self.key)}: {repr(self.val)})"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"


class SequentialSearchST(SymbolTable):
    __doc__ = f"""Implements an unordered symbol table with a linked list.
              {SymbolTable.__doc__}"""

    class _Item(_Item):
        """Custom Item for singly-linked list."""
        def __init__(self, key, value, next=None):
            super().__init__(key, value)
            self.next = next  # pointer to next item

    def __init__(self, items=None, cache=True):
        self._size = 0
        self._first = None
        super().__init__(items, cache)

    @property
    def size(self):
        return self._size

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
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
            item = self._Item(k, v, self._first)  # add new key to beginning
            self._first = item
            self._size += 1
            if self._CACHE_FLAG:
                self._cache = self._first  # update the cache

    def __getitem__(self, k):
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
        self._empty_check()
        # Perform sequential search
        x = self._first

        # Check the first node
        if k == x.key:
            self._cost = 1
            # Clear the cache and remove the item
            if self._CACHE_FLAG and self._cache and k == self._cache.key:
                self._cache = None
            self._first = x.next
            self._size -= 1
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
                self._size -= 1
                return
            else:
                i += 1
                x = x.next
        else:
            self._cost = self.size
            raise KeyError(k)

    # -------------------------------------------------------------------------
    #         Iteration
    # -------------------------------------------------------------------------
    def _make_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        def iterator(self):
            """Iterate over items."""
            q = Queue()
            x = self._first
            while x:
                q.enqueue(x.key if rtype == 'keys' else
                          (x.val if rtype == 'values' else (x.key, x.val)))
                x = x.next
            return list(q)
        return iterator


# Ex 3.1.2 unordered search with an array
# NOTE this class is implemented as an array of Item objects, but could also be
# done with parallel arrays of keys and values.
class ArrayST(SymbolTable):
    __doc__ = f"""Implements an unordered symbol table with an array.
              {SymbolTable.__doc__}"""

    def __init__(self, items=None, cache=True, selforg=False):
        self._items = list()           # Ex 3.1.2 (ArrayST)
        self._SELF_ORG_FLAG = selforg  # reorganize most recent results
        super().__init__(items, cache)

    __init__.__doc__ = (SymbolTable.__init__.__doc__ +
        """selforg : bool, optional
            If True, move each search hit to the front of the array to improve
            search times for commonly-searched keys.
        """)

    @property
    def size(self):
        """Overrides `SymbolTable.size`."""
        return len(self._items)

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
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


# Ex 3.1.12(a) Implement BST as an array of key/val objects. The original book
# implementation uses two parallel arrays for keys and values.
class BinarySearchST(OrderedSymbolTable):
    __doc__ = f"""Implements an ordered-array with binary search symbol table.
              {OrderedSymbolTable.__doc__}"""

    def __init__(self, items=None, cache=True):
        self._items = list()  # internal array of items
        # Ex 3.1.12(b) sort by keys for O(N log N) construction vs. O(N^2)
        items = mergesort(items or [])
        super().__init__(items, cache)
        self._assert_integrity()

    @property
    def size(self):
        return len(self._items)

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
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

    # -------------------------------------------------------------------------
    #         Ordered Methods
    # -------------------------------------------------------------------------
    def min(self):
        self._empty_check()
        return self._items[0].key

    def max(self):
        self._empty_check()
        return self._items[-1].key

    def floor(self, k):
        i = self.rank(k)
        if i < self.size and self._items[i].key == k:
            return self._items[i].key
        elif i > 0:
            return self._items[i-1].key
        else:
            return None

    def ceil(self, k):
        i = self.rank(k)
        if i < self.size:
            return self._items[i].key
        else:
            return None

    def rank(self, k):
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
        if 0 <= r < self.size:
            return self._items[r].key
        else:
            raise IndexError(r)

    def delete_min(self):
        self._empty_check()
        if self._CACHE_FLAG and self._cache is self._items[0]:
            self._cache = None
        del self._items[0]
        # self._assert_integrity()

    def delete_max(self):
        self._empty_check()
        if self._CACHE_FLAG and self._cache is self._items[-1]:
            self._cache = None
        del self._items[-1]
        # self._assert_integrity()

    # -------------------------------------------------------------------------
    #         Iteration
    # -------------------------------------------------------------------------
    def _make_range_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        def iterator(self, lo=None, hi=None):
            """Iterate over items with keys between `lo` and `hi`."""
            if lo is None:
                lv = 0
            else:
                lv = self.rank(lo)

            if hi is None:
                hv = self.size
            else:
                hv = self.rank(hi)
                # `hi` is included in range
                if hv < self.size and self._items[hv].key == hi:
                    hv += 1

            q = Queue()
            for x in self._items[lv:hv]:
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


# =============================================================================
# =============================================================================
