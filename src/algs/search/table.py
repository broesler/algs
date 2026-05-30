#!/usr/bin/env python3
# =============================================================================
#     File: basics.py
#  Created: 2021-03-02 09:57
#   Author: Bernie Roesler
# =============================================================================

"""Elementary Symbol Tables."""

from abc import ABC, abstractmethod

from algs.basics import Queue
from algs.sort import mergesort

__all__ = [
    'SymbolTable',
    'OrderedSymbolTable',
    'SequentialSearchST',
    'BinarySearchST',
    'ArrayST',
]


# TODO refactor ArrayST and BinarySearchST to use parallel "arrays" instead of
# a list of Item objects to be true to the book implementations, as well as
# more space efficient.


# -----------------------------------------------------------------------------
#         Define Abstract Base Classes
# -----------------------------------------------------------------------------
class SymbolTable(ABC):  # noqa: PLW1641
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

    def __init__(self, items=None, cache=False, **kwargs):
        """
        Parameters
        ----------
        items : mapping, dict-like, optional
            Iterable of (key, value) pairs to be put into the table.
        cache : bool, optional
            If True, cache the most recent search result.
        """
        self._cost = 0  # cost of previous get/put/delete
        self._CACHE_FLAG = cache  # to cache or not to cache
        self._cache = None  # store latest search hit
        # Initialize the symbol table
        items = items or []
        try:
            for k, v in items:
                self.__setitem__(k, v)
        except ValueError:
            raise ValueError(
                f"{self.__class__.__name__} expects an iterable mapping input."
            )

    # Additional constructor
    @classmethod
    def fromkeys(cls, keys=None, value=None, **kwargs):
        """Create a new table with all `keys` set to `value`."""
        keys = [] if keys is None else keys
        st = cls(**kwargs)
        for k in keys:
            st[k] = value
        return st

    @property
    @abstractmethod
    def _N(self):
        """Number of elements in the table."""
        pass

    def size(self):
        """Return the number of elements in the table."""
        return self._N

    @property
    def is_empty(self):
        """Return True if the table is empty."""
        return self.size() == 0

    def _empty_check(self):
        """General assertion that table is not empty."""
        if self.is_empty:
            raise KeyError(f"{self.__class__.__name__} is empty!")

    def __len__(self):
        return self.size()

    def __contains__(self, k):
        """Return True if `k` is present in the table, False otherwise."""
        try:
            self.__getitem__(k)
            return True
        except KeyError:
            return False

    def __eq__(self, other):
        """Return True if each table contains the same key-value pairs."""
        return sorted(self.items()) == sorted(other.items())

    def __str__(self):
        """Return the string representation of the symbol table."""

        # Define a helper function
        def kv_list(a):
            """Return a comma-separated list of key-value pairs."""
            return ', '.join(f"{repr(k)}: {repr(v)}" for k, v in a)

        # Shorten the list if there are a large number of keys
        a = self.items()
        if len(self) < 30:
            return '{' + kv_list(a) + '}'
        else:
            return '{' + kv_list(a[:3]) + ' ... ' + kv_list(a[-3:]) + '}'

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Core methods
    # -------------------------------------------------------------------------
    # Aliased methods to match with Algorithms book API
    def put(self, k, v):
        """Insert a new value `v` associated with key `k`."""
        return self.__setitem__(k, v)

    def get(self, k):
        """Return the value associated with the given key `k`."""
        return self.__getitem__(k)

    def delete(self, k):
        """Delete the item associated with `k`."""
        return self.__delitem__(k)

    def contains(self, k):
        """Return True if `k` is present in the table."""
        return self.__contains__(k)

    @abstractmethod
    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`.
        """
        pass

    @abstractmethod
    def __getitem__(self, k, v):  # noqa: PLE0302
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
        """Return an iterator over all of the keys in the table.

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
        """Return an iterator of all of the keys in the table."""
        return self._make_iterator(rtype='keys')(self)

    def values(self):
        """Return an iterator of all of the values in the table."""
        return self._make_iterator(rtype='values')(self)

    def items(self):
        """Return an iterator of all of the items in the table."""
        return self._make_iterator(rtype='items')(self)

    keys.__doc__ = _docstring.format(rtype='keys')
    values.__doc__ = _docstring.format(rtype='values')
    items.__doc__ = _docstring.format(rtype='items')

    def _make_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        return NotImplemented


class OrderedMethods(ABC):
    # An abstract class containing the ordered methods.
    # This class may not be subclassed without providing an __init__ method.

    def size(self, lo=None, hi=None):
        """Return the number of keys in the table between `lo` and `hi`, inclusive."""
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


class OrderedSymbolTable(OrderedMethods, SymbolTable):
    # Combine the unordered class with the ordered methods + iterators
    # NOTE that the `OrderedMethods` class overrides `SymbolTable.size()` to
    # accept `lo` and `hi` arguments, so `OrderedMethods` must come first.

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

    keys.__doc__ = _docstring.format(rtype='keys')
    values.__doc__ = _docstring.format(rtype='values')
    items.__doc__ = _docstring.format(rtype='items')

    def _make_range_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        return NotImplemented


# -----------------------------------------------------------------------------
#         Concrete Classes
# -----------------------------------------------------------------------------
class SequentialSearchST(SymbolTable):
    __doc__ = f"""Implements an unordered symbol table with a linked list.
              {SymbolTable.__doc__}"""

    class _Item:
        """Internal item object to hold key, value, and next pointer."""

        def __init__(self, key, value, next=None):
            self.key = key
            self.val = value
            self.next = next  # pointer to next item

        def __str__(self):
            return f"({repr(self.key)}: {repr(self.val)})"

        def __repr__(self):
            return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __init__(self, items=None, cache=True):
        self._size = 0
        self._first = None
        super().__init__(items, cache)

    @property
    def _N(self):
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
                x.val = v  # key exists, so update value
                if self._CACHE_FLAG:
                    self._cache = x
                return
            else:
                i += 1
                x = x.next
        self._cost = self.size()  # tested all the keys!
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
        self._cost = self.size()  # tested all the keys!
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
        self._cost = self.size()
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
                q.enqueue(
                    x.key
                    if rtype == 'keys'
                    else (x.val if rtype == 'values' else (x.key, x.val))
                )
                x = x.next
            return list(q)

        return iterator


# Ex 3.1.2 unordered search with parallel arrays
class ArrayST(SymbolTable):
    __doc__ = f"""Implements an unordered symbol table with an array.
              {SymbolTable.__doc__}"""

    def __init__(self, items=None, cache=True, selforg=False):
        self._keys = []  # Ex 3.1.2 (ArrayST)
        self._vals = []
        self._SELF_ORG_FLAG = selforg  # reorganize most recent results
        super().__init__(items, cache)

    __init__.__doc__ = (
        SymbolTable.__init__.__doc__
        + """selforg : bool, optional
            If True, move each search hit to the front of the array to improve
            search times for commonly-searched keys.
        """
    )

    @property
    def _N(self):
        return len(self._keys)

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
        # Check the cache (Ex 3.1.25)
        if (
            self._CACHE_FLAG
            and self._cache is not None
            and k == self._keys[self._cache]
        ):
            self._vals[self._cache] = v
            return

        # Perform sequential search
        for i, key in enumerate(self._keys):
            if k == key:
                self._cost = i + 1
                self._vals[i] = v  # key exists, so update value
                if self._CACHE_FLAG:
                    self._cache = i
                # Ex 3.1.22
                if self._SELF_ORG_FLAG:
                    if self._CACHE_FLAG:
                        self._cache = 0
                    if i > 0:
                        # Move search hit to front of the list: O(n)
                        # Cost of pop (n - (i+1)) + cost of insert(0) (n - 1)
                        self._cost += 2 * self.size() - i - 2
                        self._keys.insert(0, self._keys.pop(i))
                        self._vals.insert(0, self._vals.pop(i))
                return
        self._cost = self.size()  # tested all the keys!
        self._keys.append(k)  # add new key to end of list: O(1)
        self._vals.append(v)  # add new key to end of list: O(1)
        if self._CACHE_FLAG:
            self._cache = self.size() - 1  # update the cache

    def __getitem__(self, k):
        # Check the cache
        if (
            self._CACHE_FLAG
            and self._cache is not None
            and k == self._keys[self._cache]
        ):
            return self._vals[self._cache]

        # Perform sequential search
        for i, key in enumerate(self._keys):
            if k == key:
                self._cost = i + 1
                if self._CACHE_FLAG:
                    self._cache = i
                if self._SELF_ORG_FLAG:
                    if self._CACHE_FLAG:
                        self._cache = 0
                    if i > 0:
                        # Move search hit to front of the list: O(n)
                        self._cost += 2 * self.size() - i - 2
                        self._keys.insert(0, self._keys.pop(i))
                        self._vals.insert(0, self._vals.pop(i))
                    return self._vals[0]
                return self._vals[i]
        self._cost = self.size()  # tested all the keys!
        raise KeyError(k)

    # Exercise 3.1.5
    def __delitem__(self, k):
        # Perform sequential search
        for i, key in enumerate(self._keys):
            if k == key:
                self._cost = i + 1
                # Clear the cache and remove the item
                if self._CACHE_FLAG and self._cache is not None:
                    if k == self._keys[self._cache]:
                        self._cache = None
                    elif i < self._cache:
                        self._cache -= 1  # removed item to the left
                del self._keys[i]
                del self._vals[i]
                return
        self._cost = self.size()
        raise KeyError(k)

    # -------------------------------------------------------------------------
    #         Iterator methods
    # -------------------------------------------------------------------------
    def keys(self):
        """Return an iterator of all of the keys in the table."""
        return list(self._keys)

    def values(self):
        """Return an iterator of all of the values in the table."""
        return list(self._vals)

    def items(self):
        """Return an iterator of all of the items in the table."""
        return list(zip(self._keys, self._vals))


# Ex 3.1.12(a) Implement BST as an array of key/val objects. The original book
# implementation uses two parallel arrays for keys and values.
class BinarySearchST(OrderedSymbolTable):
    __doc__ = f"""Implements an ordered-array with binary search symbol table.
              {OrderedSymbolTable.__doc__}"""

    def __init__(self, items=None, cache=True, **kwargs):
        self._keys = []  # internal arrays of keys and values
        self._vals = []
        # Ex 3.1.12(b) sort by keys for O(N log N) construction vs. O(N^2)
        items = mergesort(items or [])
        super().__init__(items, cache, **kwargs)
        self._assert_integrity()

    @property
    def _N(self):
        return len(self._keys)

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
        # Ex 3.1.25 Check the cache
        if (
            self._CACHE_FLAG
            and self._cache is not None
            and k == self._keys[self._cache]
        ):
            self._vals[self._cache] = v
            return

        # Ex 3.1.28 If key is largest in table, slap it on the end! This
        # feature makes construction with a sorted list O(n).
        if not self.is_empty and k > self.max():
            self._keys.append(k)
            self._vals.append(k)

        # Perform binary search O(log2 N)
        i = self.rank(k)
        # if key is in the table, update the value
        if i < self.size() and self._keys[i] == k:
            self._cost += 1
            self._vals[i] = v
        else:
            # create new Item in the table
            self._cost += self.size() - i  # Θ(n-i) to move list elements
            self._keys.insert(i, k)
            self._vals.insert(i, v)

        if self._CACHE_FLAG:
            self._cache = i  # update the cache
        # self._assert_integrity()

    def __getitem__(self, k):
        # See if we have cached the key
        if (
            self._CACHE_FLAG
            and self._cache is not None
            and k == self._keys[self._cache]
        ):
            return self._vals[self._cache]

        i = self.rank(k)
        if i < self.size() and self._keys[i] == k:
            if self._CACHE_FLAG:
                self._cache = i  # cache its location
            return self._vals[i]
        else:
            raise KeyError(k)

    def __delitem__(self, k):
        i = self.rank(k)
        if i < self.size() and self._keys[i] == k:
            # Clear cache of item if necessary
            if self._CACHE_FLAG and self._cache is not None:
                if k == self._keys[self._cache]:
                    self._cache = None
                elif i < self._cache:
                    self._cache -= 1  # removed element to the left
            # Delete the item from the symbol table
            del self._keys[i]
            del self._vals[i]
            return
        else:
            raise KeyError(k)
        # self._assert_integrity()

    # -------------------------------------------------------------------------
    #         Ordered Methods
    # -------------------------------------------------------------------------
    def min(self):
        self._empty_check()
        return self._keys[0]

    def max(self):
        self._empty_check()
        return self._keys[-1]

    def floor(self, k):
        i = self.rank(k)
        if i < self.size() and self._keys[i] == k:
            return self._keys[i]
        elif i > 0:
            return self._keys[i - 1]
        else:
            return None

    def ceil(self, k):
        i = self.rank(k)
        if i < self.size():
            return self._keys[i]
        else:
            return None

    def rank(self, k):
        # Non-recursive binary search algorithm
        self._cost = 0
        lo = 0
        hi = self.size() - 1
        while lo <= hi:
            mid = (hi + lo) // 2
            self._cost += 2  # count 1 compare + 1 access here for simplicity
            if k < self._keys[mid]:
                hi = mid - 1
            elif k > self._keys[mid]:
                lo = mid + 1
            else:
                return mid
        return lo

    def select(self, r):
        if 0 <= r < self.size():
            return self._keys[r]
        else:
            raise IndexError(r)

    def delete_min(self):
        self._empty_check()
        if self._CACHE_FLAG and self._cache == 0:
            self._cache = None
        del self._keys[0]
        del self._vals[0]
        # self._assert_integrity()

    def delete_max(self):
        self._empty_check()
        if self._CACHE_FLAG and self._cache == (self.size() - 1):
            self._cache = None
        del self._keys[-1]
        del self._vals[-1]
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
                hv = self.size()
            else:
                hv = self.rank(hi)
                # `hi` is included in range
                if hv < self.size() and self._keys[hv] == hi:
                    hv += 1

            if rtype == 'keys':
                return list(self._keys[lv:hv])
            elif rtype == 'values':
                return list(self._vals[lv:hv])
            else:
                return list(zip(self._keys[lv:hv], self._vals[lv:hv]))

        return iterator

    # -------------------------------------------------------------------------
    #         Data Integrity Checks
    # -------------------------------------------------------------------------
    # Ex 3.1.30
    # NOTE integrity checks are O(N)!! They break the O(log2 N) search...
    def _assert_integrity(self):
        assert self._is_sorted() and self._rank_check()

    def _rank_check(self):
        for i in range(self.size()):
            if i != self.rank(self.select(i)):
                return False
        return True

    def _is_sorted(self):
        for i in range(1, self.size()):
            if self._keys[i - 1] > self._keys[i]:
                return False
        return True


if __name__ == "__main__":
    keys = 'SEARCHEXAMPLE'
    items = [(c, i) for i, c in enumerate(keys)]
    st = ArrayST(items, selforg=True, cache=True)
    v = st['R']

# =============================================================================
# =============================================================================
