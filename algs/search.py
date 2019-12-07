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

from recordclass import recordclass as _recordclass

from algs.basics import Queue as _Queue, _empty_check
from algs.sort import mergesort as _mergesort

__all__ = ['SequentialSearchST', 'BinarySearchST', 'BST']

# TODO
#   * make ST(ABC) to hold things like `size`, `is_empty`, `__len__` for all?
#   * use collections.abc.[Keys|Values|Items]View classes?

# Private class of key/value pairs (a mutable tuple)
_Item = _recordclass('_Item', ['key', 'value'])


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
    def __init__(self, items=list(), cache=False):
        self._items = list()
        self._CACHE_FLAG = cache  # control order of list
        self._cost = 0  # track cumulative number of compares of all operation
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
        for i, item in enumerate(self._items):
            if k == item.key:
                self._cost = i + 1
                item.value = v              # key exists, so update value
                return
        else:
            self._cost = self.size          # tested all the keys!
            self._items.append(_Item(k, v))  # add new key to end of list O(1)

    def __getitem__(self, k):
        """Return the value associated with the given key `k`."""
        # Perform sequential search
        for i, item in enumerate(self._items):
            if k == item.key:
                self._cost = i + 1
                if self._CACHE_FLAG and i > 0:
                    # move search hit to front of the list O(n)
                    self._items.insert(0, self._items.pop(i))
                return item.value
        else:
            self._cost = self.size  # tested all the keys!
            raise KeyError(k)

    def __contains__(self, k):
        """Return True if `k` is present in the table, False otherwise."""
        k in self.keys()

    def __delitem__(self, k):
        """Delete the item associated with `k`.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        for i, item in enumerate(self._items):
            if k == item.key:
                self._cost = i + 1
                del self._items[i]
                return True  # successful search
        else:
            self._cost = self.size
            raise KeyError(k)

    def __eq__(self, other):
        return sorted(self.items()) == sorted(other.items())

    def __str__(self):
        return str(dict(self._items))

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Iterator methods
    # -------------------------------------------------------------------------
    def keys(self):
        """Return an iterator of all of the keys in the table."""
        return [item.key for item in self._items]

    def values(self):
        """Return an iterator of all of the values in the table."""
        return [item.value for item in self._items]

    def items(self):
        """Return an iterator of all of the items in the table."""
        return self._items

    def __iter__(self):
        """Return an iterator of all of the keys in the table."""
        yield from self.keys()


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
        # "software cache" the most recently accessed key
        self._CACHE_FLAG = cache  # client-controlled on/off switch
        self._cache = None
        self._cost = 0        # track number of compares + array accesses
        # Initialize the symbol table
        try:
            # sort by keys so we get O(N log N) construction vs O(N^2)
            for k, v in _mergesort(items):
                self.__setitem__(k, v)
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} expects a `list` of tuples input.")

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    @property
    def size(self):
        return len(self._items)

    @property
    def is_empty(self):
        return self.size == 0

    def __len__(self):
        return self.size

    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`."""
        # If key is largest in table, slap it on the end! This feature makes
        # construction with a sorted list O(n).
        if not self.is_empty and k > self.max():
            self._items.append(_Item(k, v))

        # Perform binary search O(lg N)
        i = self.rank(k)
        # if key is in the table, update the value
        if i < self.size and self._items[i].key == k:
            self._items[i].value = v
            self._cost += 1
            return
        else:
            # create new Item in the table
            self._items.insert(i, _Item(k, v))
            self._cost += self.size - i  # Θ(n-i) to move list elements
            # self._assert_integrity()

    def __getitem__(self, k):
        """Return the value associated with the given key `k`.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        # See if we have cached the key
        if self._CACHE_FLAG and self._cache and self._cache.key == k:
            return self._cache.value

        i = self.rank(k)
        if i < self.size and self._items[i].key == k:
            if self._CACHE_FLAG:
                self._cache = self._items[i]  # cache its location
            return self._items[i].value
        else:
            raise KeyError(k)

    def __contains__(self, k):
        """Return True if `k` is present in the table, False otherwise."""
        try:
            self.__getitem__(k)
            return True
        except KeyError:
            return False

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
            if self._CACHE_FLAG and self._cache and self._cache.key == k:
                self._cache = None
            # Delete the item from the symbol table
            del self._items[i]
        else:
            raise KeyError(k)
        # self._assert_integrity()

    def min(self):
        """Return the minimum key in the table."""
        _empty_check(self)
        return self._items[0].key

    def max(self):
        """Return the maximum key in the table."""
        _empty_check(self)
        return self._items[-1].key

    def delete_min(self):
        """Delete the smallest key."""
        _empty_check(self)
        del self._items[0]
        # self._assert_integrity()

    def delete_max(self):
        """Delete the largest key."""
        _empty_check(self)
        del self._items[-1]
        # self._assert_integrity()

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

    def select(self, r):
        """Return the key of rank `r`.

        Raises
        ------
        IndexError
            If there are fewer than `r`+1 keys in the table.
        """
        return self._items[r].key

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

    def __eq__(self, other):
        return self.items() == sorted(other.items())

    def __str__(self):
        return str(dict(self._items))

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Iterator functions
    # -------------------------------------------------------------------------
    docstring = """Return an in-order iterator over the {rtype} between the keys `lo`
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

    keys.__doc__   = docstring.format(rtype='keys')
    values.__doc__ = docstring.format(rtype='values')
    items.__doc__  = docstring.format(rtype='items')

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
                          (x.value if rtype == 'values' else x))
            return list(q)
        return iterator

    # -------------------------------------------------------------------------
    #         Data Integrity Checks
    # -------------------------------------------------------------------------
    # NOTE integrity checks are O(N)!! They break the O(lg N) search...
    def _assert_integrity(self):
        assert self._rank_check() and self._is_sorted()

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
    """Implements a binary search tree data structure.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) tuples to be put onto the tree.

    Attributes
    ----------
    size : int
        Number of items on the tree.
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
            self.height = 1  # height of the tree rooted at this _Node

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
    def __init__(self, items=list()):
        self._root = None
        try:
            for k, v in items:
                self._root = self._set(k, v, self._root)
            return
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} expects a `list` of tuples input.")

    @property
    def size(self):
        return self._size(self._root)

    @property
    def height(self):
        """Return the height of the BST in O(1) time."""
        return self._height(self._root)

    @property
    def is_empty(self):
        return self.size == 0

    def __len__(self):
        return self.size

    def __getitem__(self, k):
        """Return the value associated with the given `k`."""
        return self._get(k, self._root)

    def __setitem__(self, k, v):
        """Add a new node to subtree at `x`, associating `k` with `v`.
        If `k` is in subtree rooted at `x`, change its value to `v`."""
        return self._set(k, v, self._root)

    def __delitem__(self, k):
        """Delete the node associated with `k`."""
        self._root = self._delete(k, self._root)

    def __contains__(self, k):
        """Return True if `k` is present in the tree, False otherwise."""
        return self.__getitem__(k) is not None

    def __eq__(self, other):
        return self.items() == sorted(other.items())

    def __str__(self):
        return str(dict(self.items()))

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Other Public Methods
    # -------------------------------------------------------------------------
    # TODO refactor s.t. min/max/floor/ceil all return Nodes. Client can choose
    # to use key or value. Returning Nodes will save a separate private method
    # definition.
    def min(self):
        """Return the minimum key in the tree."""
        _empty_check(self)
        return self._min(self._root).key

    def max(self):
        """Return the maximum key in the tree."""
        _empty_check(self)
        return self._max(self._root).key

    def floor(self, k):
        """Return the largest key less than or equal to `k`, or None if `k` is
        less than the smallest key in the table."""
        x = self._floor(k, self._root)  # self._floor returns a Node
        return x.key if x else None

    def ceil(self, k):
        """Return the smallest key greater than or equal to `k`, or None if `k`
        is greater than the largest key in the table."""
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
        """Delete the smallest key."""
        _empty_check(self)
        self._root = self._delete_min(self._root)

    def delete_max(self):
        """Delete the largest key."""
        _empty_check(self)
        self._root = self._delete_max(self._root)

    def height_r(self):
        """Determine the height of the BST recursively, in O(n) time."""
        return self._height_r(self._root)

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
    def _size(self, x=None):
        """Return the size of the subtree rooted at Node `x`."""
        return 0 if x is None else x.N

    def _get(self, k, x=None):
        """Return the value associated with the given `k`.

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
            return x.val

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
        elif k > x.key:
            x.right = self._set(k, v, x.right)
        else:  # k == x.key
            x.val = v  # update the value

        # Update the size of the subtree located at the given root
        x.N = self._size(x.left) + self._size(x.right) + 1
        x.height = max(self._height(x.left), self._height(x.right)) + 1
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

    def _delete_min(self, x=None):
        """Delete the minimum key in the subtree rooted at `x`."""
        if x.left is None:
            return x.right
        x.left = self._delete_min(x.left)
        # Update the size of the subtree located at the given root
        x.N = self._size(x.left) + self._size(x.right) + 1
        return x

    def _delete_max(self, x=None):
        """Delete the maximum key in the subtree rooted at `x`."""
        if x.right is None:
            return x.left
        x.right = self._delete_max(x.right)
        # Update the size of the subtree located at the given root
        x.N = self._size(x.left) + self._size(x.right) + 1
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
            if x.right is None:
                return x.left
            # save pointer to Node to be deleted
            t = x
            # Get the successor to the node to be deleted
            x = self._min(t.right)
            x.right = self._delete_min(t.right)
            x.left = t.left
        # Update the size of the subtree located at the given root
        x.N = self._size(x.left) + self._size(x.right) + 1
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

    def _level_order(self):
        """Return an iterator over the keys in level-order (breadth-first)."""
        keys = _Queue()
        q = _Queue()
        q.enqueue(self._root)
        while q:
            x = q.dequeue()
            if x is None:
                continue
            keys.enqueue(x.key)
            q.enqueue(x.left)
            q.enqueue(x.right)
        return list(keys)

    # -------------------------------------------------------------------------
    #         Iterator functions
    # -------------------------------------------------------------------------
    docstring = """Return an in-order iterator over the {rtype} between the keys `lo`
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

    keys.__doc__   = docstring.format(rtype='keys')
    values.__doc__ = docstring.format(rtype='values')
    items.__doc__  = docstring.format(rtype='items')

    def __iter__(self):
        yield from self.keys()

    # factory for generic in-order iteration over keys
    def _make_inorder_iterator(self, rtype):
        """Create an iterator over the desired type."""
        def iterator(self, lo=None, hi=None):
            try:
                if lo is None:
                    lo = self.min()
                if hi is None:
                    hi = self.max()
            except IndexError:
                return list()
            else:
                return self._iterate(lo, hi, x=self._root, rtype=rtype)
        return iterator

    def _iterate(self, lo, hi, x=None, q=None, rtype='keys'):
        """Recursively add items to the given _Queue."""
        # Defaults
        if x is None:
            return
        if q is None:
            q = _Queue()
        # Enqueue by key order
        if lo < x.key:
            self._iterate(lo, hi, x.left, q, rtype)
        if lo <= x.key and hi >= x.key:
            q.enqueue(x.key if rtype == 'keys' else (x.val if rtype == 'values' else _Item(x.key, x.val)))
        if hi > x.key:
            self._iterate(lo, hi, x.right, q, rtype)
        return list(q)


class BST_nr():
    """Implements a binary search tree data structure, non-recursively.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) tuples to be put onto the tree.

    Attributes
    ----------
    size : int
        Number of items on the tree.
    is_empty : bool
        True if `size == 0`.
    """
    # Private Node class
    class _Node():
        """Internal node object to hold key, value, and two children.

        Attributes
        ----------
        key : object
            Any hashable value.
        val : object
            Any object to be associated with the key.
        left, right : _Node
            Pointers to children nodes in the tree.
        N : int
            The number of nodes in the subtree rooted at this node.
        height : int
            The height of subtree rooted at this node. Height is defined by the
            longest path from root to leaf, O(lg N).
        """
        def __init__(self, key, value=None):
            self.key = key
            self.val = value
            self.left = self.right = None
            self.N = 1       # nodes in subtree rooted here
            self.height = 1  # height of the tree rooted at this _Node

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
    def __init__(self, items=list()):
        self._root = None
        try:
            for k, v in items:
                self.__setitem__(k, v)
            return
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} expects a `list` of tuples input.")

    @property
    def size(self):
        """Return the number of nodes in the BST."""
        return self._size(self._root)

    @property
    def height(self):
        """Return the height of the BST in O(1) time."""
        return 0 if self._root is None else self._root.height

    @property
    def is_empty(self):
        return self.size == 0

    def __len__(self):
        return self.size

    def __getitem__(self, k):
        """Return the value associated with the given `k`.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        x = self._root
        while x:
            if k == x.key:
                return x.val
            elif k < x.key:
                x = x.left
            else:
                x = x.right
        raise KeyError(k)

    def __setitem__(self, k, v):
        """Add a new node to subtree at `x`, associating `k` with `v`.
        If `k` is in subtree rooted at `x`, change its value to `v`."""
        x = p = self._root
        while x:
            p = x  # track parent node
            if k == x.key:
                x.val = v  # update the value if found
                return
            elif k < x.key:
                x = x.left
            else:
                x = x.right

        # Insert new node as child of parent
        if p is None:
            self._root = self._Node(k, v)
        elif k < p.key:
            p.left = self._Node(k, v)
        else:
            p.right = self._Node(k, v)

        # Need 2nd pass to update _Node counts
        x = self._root
        while x:
            if k == x.key:
                return
            elif k < x.key:
                x.N += 1
                x = x.left
            else:
                x.N += 1
                x = x.right

    def __delitem__(self, k):
        """Delete the node associated with `k`."""
        self._root = self._delete(k, self._root)

    def __contains__(self, k):
        """Return True if `k` is present in the tree, False otherwise."""
        return self.__getitem__(k) is not None

    def __eq__(self, other):
        return self.items() == sorted(other.items())

    def __str__(self):
        return str(dict(self.items()))

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Other Public Methods
    # -------------------------------------------------------------------------
    # TODO refactor s.t. min/max/floor/ceil all return Nodes. 
    def min(self):
        """Return the minimum key in the tree."""
        _empty_check(self)
        x = self._root
        while x.left:
            x = x.left
        return x.key

    def max(self):
        """Return the maximum key in the tree."""
        _empty_check(self)
        x = self._root
        while x.right:
            x = x.right
        return x.key

    def floor(self, k):
        """Return the largest key less than or equal to `k`, or None if `k` is
        less than the smallest key in the table.
        """
        x = self._root
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
        return p.key if p else None

    def ceil(self, k):
        """Return the smallest key greater than or equal to `k`, or None if `k`
        is greater than the largest key in the table.
        """
        x = self._root
        p = None  # pointer to the floor Node
        while x:
            if k == x.key:
                p = x
                break
            elif k > x.key:
                x = x.right  # floor must be in right subtree
            else:
                p = x       # keep pointer to parent
                x = x.left
        return p.key if p else None

    def rank(self, k):
        """Return the number of keys less than `k`.
        .. note:: `rank` is the inverse of `select`.
        """
        r = 0
        x = self._root
        while x:
            if k == x.key:
                r += self._size(x.left)
                break
            elif k < x.key:
                x = x.left
            else:
                r += 1 + self._size(x.left)
                x = x.right
        return r

    def select(self, r):
        """Return the key of rank `r`.

        .. note:: `select` is the inverse of `rank`.

        Raises
        ------
        IndexError
            If there are fewer than `r`+1 keys in the table.
        """
        _empty_check(self)
        x = self._root
        rank = r
        while x:
            t = self._size(x.left)
            if t > rank:
                x = x.left
            elif t < rank:
                rank -= (t + 1)
                x = x.right
            else:
                return x.key
        else:
            raise IndexError(r)

    def delete_min(self):
        """Delete the smallest key."""
        _empty_check(self)
        x = self._root
        if x.left is None:  # the min is the root
            self._root = x.right
            return
        # find the min and delete the pointer to it
        while x.left:
            p = x
            p.N -= 1
            x = x.left
        p.left = x.right

    def delete_max(self):
        """Delete the largest key."""
        _empty_check(self)
        x = self._root
        if x.right is None:  # the max is the root
            self._root = x.left
            return
        # find the max and delete the pointer to it
        while x.right:
            p = x
            p.N -= 1
            x = x.right
        p.right = x.left

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
    def _size(self, x=None):
        """Return the size of the subtree rooted at Node `x`."""
        return 0 if x is None else x.N

    def _min(self, x=None):
        """Return the minimum key in the subtree rooted at `x`."""
        return x if x.left is None else self._min(x.left)

    def _delete_min(self, x=None):
        """Delete the minimum key in the subtree rooted at `x`."""
        if x.left is None:
            return x.right
        x.left = self._delete_min(x.left)
        # Update the size of the subtree located at the given root
        x.N = self._size(x.left) + self._size(x.right) + 1
        return x

    # TODO
    #   * implement `delete` non-recursively
    #   * delete `_min`, `_delete_min` methods
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
            if x.right is None:
                return x.left
            # save pointer to Node to be deleted
            t = x
            # Get the successor to the node to be deleted
            x = self._min(t.right)
            x.right = self._delete_min(t.right)
            x.left = t.left
        # Update the size of the subtree located at the given root
        x.N = self._size(x.left) + self._size(x.right) + 1
        return x

    # TODO implement pre- and post-order traversals
    def _level_order(self):
        """Return an iterator over the keys in level-order (breadth-first)."""
        keys = _Queue()
        q = _Queue()
        q.enqueue(self._root)
        while q:
            x = q.dequeue()
            if x is None:
                continue
            keys.enqueue(x.key)
            q.enqueue(x.left)
            q.enqueue(x.right)
        return list(keys)

    # -------------------------------------------------------------------------
    #         Iterator functions
    # -------------------------------------------------------------------------
    docstring = """Return an in-order iterator over the {rtype} between the keys `lo`
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

    keys.__doc__   = docstring.format(rtype='keys')
    values.__doc__ = docstring.format(rtype='values')
    items.__doc__  = docstring.format(rtype='items')

    def __iter__(self):
        yield from self.keys()

    # factory for generic in-order iteration over keys
    def _make_inorder_iterator(self, rtype):
        """Create an iterator over the desired type."""
        def iterator(self, lo=None, hi=None):
            try:
                if lo is None:
                    lo = self.min()
                if hi is None:
                    hi = self.max()
            except IndexError:
                return list()
            else:
                return self._iterate(lo, hi, x=self._root, rtype=rtype)
        return iterator

    def _iterate(self, lo, hi, x=None, q=None, rtype='keys'):
        """Recursively add items to the given _Queue."""
        # Defaults
        if x is None:
            return
        if q is None:
            q = _Queue()
        # Enqueue by key order
        if lo < x.key:
            self._iterate(lo, hi, x.left, q, rtype)
        if lo <= x.key and hi >= x.key:
            q.enqueue(x.key if rtype == 'keys' else (x.val if rtype == 'values' else _Item(x.key, x.val)))
        if hi > x.key:
            self._iterate(lo, hi, x.right, q, rtype)
        return list(q)



# -----------------------------------------------------------------------------
#         Test Functions
# -----------------------------------------------------------------------------
# TODO move to proper unit testing script
if __name__ == '__main__':
    import numpy as np

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
        while True:
            try:
                getattr(container, op)(*args)  # call the method
            except err_type:
                return
            except Exception as err:
                fails += 1
                print(f"Raised: {repr(err)}, Expected: {err_type}")
                raise err

    # Prepare test data
    test_str = 'SEARCHEXAMPLE'
    test_set = set(test_str)
    data = [(c, i) for i, c in enumerate(test_str)]
    data_set = data.copy()
    data_set.remove(('E', 1))
    data_set.remove(('A', 2))
    data_set.remove(('E', 6))

    # ---------- Test SequentialSearchST ----------
    # TODO implement tests for t._cost after various operations
    st = SequentialSearchST()
    should_be(st.size, 0)
    should_be(st.is_empty, True)
    should_be(st.keys(),   [])
    should_be(st.values(), [])
    should_be(st.items(),  [])

    st = SequentialSearchST(data)
    for k, v in data:
        if k == 'E' or k == 'A':
            should_be(st[k], max([v for key, v in data if key == k]))
        else:
            should_be(st[k], v)

    should_be(len(st), len(test_set))  # test __len__
    should_be(len(st), st.size)
    # st.keys() not guaranteed in order, so these tests are weak
    should_be(sorted(st.keys()), sorted(test_set))
    should_be((st.keys() == sorted(test_set)), False)  # not inserted in order
    should_be(sorted(st.values()), sorted([v for k, v in data_set]))
    should_be(sorted([(x.key, x.value) for x in st.items()]), sorted(data_set))

    err_test(st, '__getitem__', 'Z', err_type=KeyError)

    v = st['A']
    del st['A']
    should_be(sorted(st.keys()), sorted(test_set - set('A')))
    st['A'] = v

    # Test self-organizing search
    tc = SequentialSearchST(data, cache=True)
    for k in np.random.choice(tc.keys(), size=tc.size):
        tc[k]                       # search for the key
        should_be(tc.keys()[0], k)  # should get moved to front
        tc[k]                       # search again
        should_be(tc._cost, 1)      # test cost

    # ---------- Test Ordered STs ----------
    for ST in [BST_nr]:  # BST
    # for ST in [BinarySearchST, BST, BST_nr]:
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

        # Test construction by list of tuples
        t = ST(data)
        # t._assert_integrity()  # TODO implement for BST(_nr)?

        # Binary Search Tree:
        #  height
        #  6        S
        #          / \
        #  5      E   X
        #      /    \
        #  4  A      R
        #      \    /
        #  3    C  H
        #           \
        #  2         M
        #           / \
        #  1       L   P

        should_be(len(t), len(test_set))  # test __len__
        should_be(len(t), t.size)

        for k, v in data:
            should_be(k in t, True)  # test __contains__

            # test __get__
            if k == 'E' or k == 'A':
                should_be(t[k], max([v for key, v in data if key == k]))
            else:
                should_be(t[k], v)

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

        # BST-specific tests
        if isinstance(t, BST):
            should_be(t.height, 6)      # Node attribute method, as a property
            should_be(t.height_r(), 6)  # recursive method
            should_be(list(t._level_order()), list('SEXARCHMLP'))

        # In-order traversal
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
        for i, c in enumerate(sorted(test_set - set('A'))):
            should_be(t.select(i), c)
            should_be(t.rank(c), i)
        t[k] = v  # replace value

        k, v = t.max(), t[t.max()]
        t.delete_max()  # remove 'X'
        should_be(t.max(), 'S')
        # Test updated ranks
        for i, c in enumerate(sorted(test_set - set('X'))):
            should_be(t.select(i), c)
            should_be(t.rank(c), i)
        t[k] = v  # replace value

        # Delete arbitrary key
        v = t['E']
        del t['E']
        should_be(len(t), len(test_set)-1)
        err_test(t, '__getitem__', 'E', err_type=KeyError)
        t['E'] = v

        if isinstance(t, BST):
            # delete the root
            v = t['S']
            del t['S']
            should_be(t._root.key, 'X')
            t['S'] = v

    # Test comparisons between objects (in *both* directions)
    should_be(SequentialSearchST(data), BinarySearchST(data))
    should_be(BinarySearchST(data), SequentialSearchST(data))
    should_be(BinarySearchST(data), BST(data))
    should_be(BST(data), BinarySearchST(data))

    # Summary
    if fails > 0:
        print(f"{fails}/{tests} tests failed")
    else:
        print(f"All {tests} tests passed!")

# =============================================================================
# =============================================================================
