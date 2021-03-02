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
                        Queue as _Queue
from algs.search.table import _empty_check

__all__ = ['BST', 'BST_nr', 'ThreadedST', 'ThreadedST_nr', 'ArrayBST']


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
    # Deletion method value is constant with the class
    _THRESH = dict({'Hibbard': 1, 'Hibbard_p': 0, 'random': 0.5})

    # Private Node class
    class _Node():
        """Internal node object to hold key, value, and two children."""
        def __init__(self, key, value=None):
            self.key = key
            self.val = value
            self.left = self.right = None
            self.N = 1       # nodes in subtree rooted here
            self.height = 1  # Ex 3.2.6(b) height of the tree rooted at _Node
            self.ipl = 0     # Ex 3.2.47 sum of depths of nodes in subtree

        def __str__(self):
            # Avoid recursion through entire tree!! Just print each child
            left_str = f"{{{repr(self.left.key)}: {repr(self.left.val)}}}" \
                        if self.left else 'None'
            right_str = f"{{{repr(self.right.key)}: {repr(self.right.val)}}}" \
                        if self.right else 'None'
            return f"{{{repr(self.key)}: {repr(self.val)}}}, "\
                   f"L:{left_str}, R:{right_str}, N={self.N}"

        def __repr__(self):
            return f"<{self.__class__.__name__}: {self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __init__(self, items=list(), cache=True, delete_method='Hibbard'):
        self._root = None
        self._CACHE_FLAG = cache       # Ex 3.2.28
        self._cache = None             # store the most recently accessed Node.
        self._cost = 0                 # Ex 3.2.39, 3.2.40, 3.2.44, 3.2.47

        try:
            self._RAND_THRESH = self._THRESH[delete_method]
        except KeyError:
            raise ValueError(f"Invalid delete_method '{delete_method}'!")

        try:
            for k, v in items:
                self._root = self._set(k, v, self._root)
            return
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             'expects an iterable mapping input.')

    # Add to make BST behave more like python dict
    @classmethod
    def fromkeys(cls, keys=list(), value=None, **kwargs):
        """Create a new BST with keys from iterable and values set to value."""
        st = cls(**kwargs)
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

    def __delitem__(self, k):
        """Delete the node associated with `k`.

        ..note:: Implements eager Hibbard deletion.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        self._root = self._delete(k, self._root)
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
        KeyError
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
        KeyError
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
                raise TypeError('pop expected at most 2 arguments, '
                                f"got {len(args)+1}")

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

    # Idea: replace `random.random()` with `self._poss_arrow` and flip it on
    # each deletion.
    def _delete(self, k, x=None):
        """Delete the node associated with `k` by choosing the predecessor or
            successor at random.

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
        if x is None:
            raise KeyError(k)

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
                if random.random() < self._RAND_THRESH:
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
        if lo or hi:
            return self._make_range_iterator(rtype='keys')(self, lo, hi)
        else:
            return self._make_inorder_iterator(rtype='keys')(self)

    def values(self, lo=None, hi=None):
        if lo or hi:
            return self._make_range_iterator(rtype='values')(self, lo, hi)
        else:
            return self._make_inorder_iterator(rtype='values')(self)

    def items(self, lo=None, hi=None):
        if lo or hi:
            return self._make_range_iterator(rtype='items')(self, lo, hi)
        else:
            return self._make_inorder_iterator(rtype='items')(self)

    keys.__doc__   = _docstring.format(rtype='keys')
    values.__doc__ = _docstring.format(rtype='values')
    items.__doc__  = _docstring.format(rtype='items')

    # factory for generic in-order iteration over keys
    def _make_range_iterator(self, rtype):
        """Create an iterator over the desired type."""
        def iterator(self, lo=None, hi=None):
            try:
                if lo is None:
                    lo = self.min()
                if hi is None:
                    hi = self.max()
                return self._iterate_range(lo, hi, x=self._root, rtype=rtype)
            except KeyError:
                return list()
        return iterator

    def _iterate_range(self, lo, hi, x=None, q=None, rtype='keys'):
        """Recursively range search the BST for keys between `lo` and `hi`."""
        if x is None:
            return
        if q is None:
            q = _Queue()
        # Enqueue by key order
        if lo < x.key:
            self._iterate_range(lo, hi, x.left, q, rtype)
        if lo <= x.key <= hi:
            q.enqueue(x.key if rtype == 'keys' else
                      (x.val if rtype == 'values' else (x.key, x.val)))
        if hi > x.key:
            self._iterate_range(lo, hi, x.right, q, rtype)
        return list(q)

    # factory for generic in-order iteration *without* ranges
    def _make_inorder_iterator(self, rtype):
        """Create an iterator over the desired type."""
        def iterator(self):
            if self._root is None:
                return list()
            else:
                return self._iterate_all(x=self._root, rtype=rtype)
        return iterator

    #  more efficient than `yield from self.keys()` for entire traversal since
    #  we don't have to find the min or max keys
    def _iterate_all(self, x=None, q=None, rtype='keys'):
        """Recursively traverse the tree in order (depth-first search)."""
        if x is None:
            return
        if q is None:
            q = _Queue()
        # Yield rtype in order
        self._iterate_all(x.left, q, rtype)
        q.enqueue(x.key if rtype == 'keys' else
                  x.val if rtype == 'values' else (x.key, x.val))
        self._iterate_all(x.right, q, rtype)
        return list(q)

    # iterate as a generator function
    def __iter__(self):
        yield from self.keys()

    # Tree traversals (could write with `yield` statements instead)
    def pre_order(self):
        """Iterate over the keys in pre-order (depth-first)."""
        return self._pre_order(self._root)

    def _pre_order(self, x=None, q=None):
        """Iterate over the keys in pre-order (depth-first)."""
        if x is None:
            return
        if q is None:
            q = _Queue()
        q.enqueue(x.key)
        self._pre_order(x.left, q)
        self._pre_order(x.right, q)
        return list(q)

    def post_order(self):
        """Iterate over the keys in post-order (depth-first)."""
        return self._post_order(self._root)

    def _post_order(self, x=None, q=None):
        """Iterate over the keys in post-order (depth-first)."""
        if x is None:
            return
        if q is None:
            q = _Queue()
        self._post_order(x.left, q)
        self._post_order(x.right, q)
        q.enqueue(x.key)
        return list(q)

    def reverse(self):
        """Reverse the BST recursively."""
        return self._reverse(self._root)

    def _reverse(self, x=None):
        """Reverse the BST recursively."""
        if x is None:
            return

        # Swap the children
        # x.left, x.right = x.left, x.right
        temp = x.left
        x.left = x.right
        x.right = temp
        # Do it for each subtree
        self._reverse(x.left)
        self._reverse(x.right)

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
        p = None
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

                if random.random() < self._RAND_THRESH:
                    # Get successor to the node to be deleted
                    x = t.next
                    x.right = self._delete_min(t.right)
                    x.left = t.left
                else:
                    # take predecessor
                    x = t.prev
                    x.left = self._delete_max(t.left)
                    x.right = t.right

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

    # -------------------------------------------------------------------------
    #         Iterator
    # -------------------------------------------------------------------------
    def _iterate_range(self, lo, hi, x=None, q=None, rtype='keys'):
        """Recursively range search the BST for keys between `lo` and `hi`."""
        if x is None:
            return
        # start the recursion with the mininmum
        return self.__iterate_range(lo, hi, x=self._min(x), rtype=rtype)

    def __iterate_range(self, lo, hi, x=None, q=None, rtype='keys'):
        """Recursively range search the BST for keys between `lo` and `hi`."""
        if x is None:
            return
        if q is None:
            q = _Queue()
        # Enqueue by key order
        if lo <= x.key <= hi:
            q.enqueue(x.key if rtype == 'keys' else
                      (x.val if rtype == 'values' else (x.key, x.val)))
        elif x.key > hi:
            return list(q)  # no need to look at further nodes
        self.__iterate_range(lo, hi, x.next, q, rtype)
        return list(q)

    def _iterate_all(self, x=None, rtype='keys'):
        """Recursively traverse the tree in order from the minimum."""
        if x is None:
            return
        # start the recursion with the mininmum
        return self.__iterate_all(x=self._min(x), rtype=rtype)

    def __iterate_all(self, x=None, q=None, rtype='keys'):
        """Recursively traverse the tree in order (depth-first search)."""
        if x is None:
            return
        if q is None:
            q = _Queue()
        # Yield rtype in order
        q.enqueue(x.key if rtype == 'keys' else
                  x.val if rtype == 'values' else (x.key, x.val))
        self.__iterate_all(x.next, q, rtype)
        return list(q)


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
            if random.random() < self._RAND_THRESH:
                # take successor
                x = self._min(t.right)
                s.push(x)
                x.right = self._delete_min(t.right)
                x.left = t.left
            else:
                # take predecessor
                x = self._max(t.left)
                s.push(x)
                x.left = self._delete_max(t.left)
                x.right = t.right

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
        """Return node with the minimum key in the subtree rooted at `x`."""
        while x.left:
            x = x.left
        return x

    def _max(self, x):
        """Return node with the maximum key in the subtree rooted at `x`."""
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
    def _iterate_range(self, lo, hi, rtype='keys', **kwargs):
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

    # Overwrite BST._iterate_all recursive function
    def _iterate_all(self, rtype='keys', **kwargs):
        """Add items to a Queue, in key-order over all keys."""
        q = _Queue()    # the output queue
        s = _Stack()    # visited nodes so we can pop back up the tree
        x = self._root
        while s or x:
            # Move left until `lo` is found
            if x is not None:
                s.push(x)
                x = x.left
            else:
                if x is None:
                    x = s.pop()
                q.enqueue(x.key if rtype == 'keys' else
                            (x.val if rtype == 'values' else (x.key, x.val)))
                x = x.right
        return list(q)


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
            if random.random() < self._RAND_THRESH:
                # get successor
                x = t.next
                s.push(x)
                x.right = self._delete_min(t.right)
                x.left = t.left
            else:
                # get predecessor
                x = t.prev
                s.push(x)
                x.left = self._delete_max(t.left)
                x.right = t.right

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
    #         Iterators
    # -------------------------------------------------------------------------
    def _iterate_range(self, lo, hi, rtype='keys', **kwargs):
        """Add items to a Queue, in key-order from `lo` to `hi`."""
        q = _Queue()               # the output queue
        x = self._min(self._root)  # get the minimum Node
        while x:
            if lo > x.key:
                x = x.next
            elif lo <= x.key <= hi:
                q.enqueue(x.key if rtype == 'keys' else
                            (x.val if rtype == 'values' else (x.key, x.val)))
                x = x.next
            else:  # x.key > hi
                break
        return list(q)

    def _iterate_all(self, rtype='keys', **kwargs):
        """Add all items to a Queue, in key-order."""
        q = _Queue()               # the output queue
        x = self._min(self._root)  # get the minimum Node
        while x:
            q.enqueue(x.key if rtype == 'keys' else
                      (x.val if rtype == 'values' else (x.key, x.val)))
            x = x.next
        return list(q)


# Ex 3.2.41 array representation
class ArrayBST():
    """Implements a binary search tree represented by parallel arrays.

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
    def __init__(self, items=list(), cache=True):
        self._root = None      # index of the information on the root
        self._keys = list()
        self._vals = list()
        self._lefts = list()   # indices of left-links
        self._rights = list()  # indices of right-links
        self._CACHE_FLAG = cache
        self._cache = None
        self._cost = 0
        try:
            for k, v in items:
                self._root = self.__setitem__(k, v)
            return
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             'expects an iterable mapping input.')

    @property
    def size(self):
        return len(self._keys)

    @property
    def is_empty(self):
        return self.size == 0

    def __len__(self):
        return self.size

    def __getitem__(self, k):
        """Return the value associated with the given key `k`."""
        if self.is_empty:
            raise KeyError(k)

        x = self._root
        while x is not None:
            if k < self._keys[x]:
                x = self._lefts[x]
            elif k > self._keys[x]:
                x = self._rights[x]
            else:  # k == self._keys[x]:
                if self._CACHE_FLAG:
                    self._cache = x
                return self._vals[x]
        else:
            raise KeyError(k)

    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`."""
        p = x = self._root
        while x is not None:
            p = x
            if k == self._keys[x]:
                self._vals[x] = v
                if self._CACHE_FLAG:
                    self._cache = x
                return self._root
            else:
                # Move down the tree
                if k < self._keys[x]:
                    x = self._lefts[x]
                else:
                    x = self._rights[x]

        # Insert new node as child of parent
        if p is None:
            self._root = self._new_node(k, v)
            cache = self._root
        elif k < self._keys[p]:
            self._lefts[p] = self._new_node(k, v)
            cache = self._lefts[p]
        else:
            self._rights[p] = self._new_node(k, v)
            cache = self._rights[p]

        if self._CACHE_FLAG:
            self._cache = cache

        return self._root

    def __delitem__(self, k):
        """Delete the item associated with `k`."""
        pass

    def __contains__(self, k):
        """Return True if `k` is present in the tree, False otherwise."""
        try:
            self.__getitem__(k)
            return True
        except KeyError:
            return False

    # NOTE no guarantees on order of keys in output yet
    def keys(self):
        return self._keys

    def values(self):
        return self._vals

    def items(self):
        return list(zip(self._keys, self._vals))

    def __iter__(self):
        yield from self.keys()

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
    def _new_node(self, k, v):
        """Add a new node to the tree."""
        self._keys.append(k)
        self._vals.append(v)
        self._lefts.append(None)
        self._rights.append(None)
        return self.size - 1  # index of the new node

# =============================================================================
# =============================================================================
