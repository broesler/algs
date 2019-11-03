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

from algs.basics import Queue

__all__ = ['BST']


class BST():
    """Implements a binary search tree data structure.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) pairs to be put onto the tree.

    Attributes
    ----------
    size : int
        Number of items on the tree.
    is_empty : bool
        True if `size == 0`.

    .. note: `get` and `set` are achieved via python builtins

    Example
    -------
    >>> t = BST()
    >>> t['A'] = 0
    >>> t['B'] = 1
    >>> t['C'] = 2
    >>> t['A'] = 10
    >>> t.min()
    'A'
    >>> t['A']
    10
    """
    # Private Node class
    class _Node():
        """Internal node object to hold key, value, and two children."""
        def __init__(self, key, value=None):
            self.key = key
            self.val = value
            self.left = None
            self.right = None
            self.N = 1  # nodes in subtree rooted here

        def __str__(self):
            # Avoid recursion through entire tree!! Just print each child
            left_str = f"({self.left.key}, {self.left.val})" if self.left else 'None'
            right_str = f"({self.right.key}, {self.right.val})" if self.right else 'None'
            return f"({self.key}, {self.val}), L:{left_str}, R:{right_str}, N={self.N}"

        def __repr__(self):
            return f"<{self.__class__.__name__}: {self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __init__(self, items=dict()):
        self._root = None

        # Dictionary construction
        try:
            for k, v in items.items():
                self._root = self.__setitem__(k, v, self._root)
            return
        except AttributeError:
            pass

        # List of tuples construction
        try:
            for v in items:
                self._root = self.__setitem__(v[0], v[1], self._root)
            return
        except IndexError:
            raise Exception('Input format not supported!')

    @property
    def size(self):
        return self._size(self._root)

    @property
    def is_empty(self):
        return self.size == 0

    def __len__(self):
        return self.size

    def __getitem__(self, k, x=1):
        """Return the value associated with the given `k`.

        Parameters
        ----------
        k : key
            key for which to search
        x : _Node, optional
            root of the subtree at which to begin search
        """
        # Set a default sentinel to save us a separate function definition
        if x == 1:
            x = self._root

        # got to the bottom of the tree, key not found
        if x is None:
            return

        if k < x.key:
            return self.__getitem__(k, x.left)
        elif k > x.key:
            return self.__getitem__(k, x.right)
        else:  # k == root.key!
            return x.val

    def __setitem__(self, k, v, x=1):
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
        # Set a default sentinel to save us a separate function definition
        if x == 1:
            x = self._root

        # subtree is empty, create a new node
        if x is None:
            return self._Node(k, v)

        # create a child, or update the value
        if k < x.key:
            x.left = self.__setitem__(k, v, x.left)
        elif k > x.key:
            x.right = self.__setitem__(k, v, x.right)
        else:  # k == x.key
            x.val = v  # update the value

        # Update the size of the subtree located at the given root
        x.N = self._size(x.left) + self._size(x.right) + 1
        return x

    def __delitem__(self, k):
        """Delete the node associated with `k`."""
        self._root = self._delete(k, self._root)

    def __contains__(self, k):
        """Return True if `k` is present in the tree, False otherwise."""
        return self.__getitem__(k) is not None

    def __iter__(self):
        yield from self.keys()

    def __str__(self):
        return str(self._root)

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
        return self._min(self._root).key

    def max(self):
        """Return the maximum key in the tree."""
        return self._max(self._root).key

    def floor(self, k):
        """Return the largest key less than or equal to `k`."""
        x = self._floor(k, self._root)  # self._floor returns a Node
        return x.key if x else None

    def ceil(self, k):
        """Return the smallest key greater than or equal to `k`."""
        x = self._ceil(k, self._root)  # self._ceil returns a Node
        return x.key if x else None

    def rank(self, k):
        """Return the number of keys less than `k`."""
        return self._rank(k, self._root)

    def select(self, k):
        """Return the key of rank `k`."""
        return self._select(k, self._root).key

    def delete_min(self):
        """Delete the smallest key."""
        self._root = self._delete_min(self._root)

    def delete_max(self):
        """Delete the largest key."""
        self._root = self._delete_max(self._root)

    def keys(self, lo=None, hi=None):
        """Return an in-order iterator over the keys."""
        if lo is None:
            lo = self.min()
        if hi is None:
            hi = self.max()
        q = self._keys(lo, hi, x=self._root)
        return iter(q)

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
    def _size(self, x=None):
        """Return the size of the subtree rooted at Node `x`."""
        if x is None:
            return 0
        else:
            return x.N

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

    def _select(self, k, x=None):
        """Return the Node that has rank `k` in the subtree rooted at `x`.

        .. note:: `select` is the inverse of `rank`."""
        if x is None:
            return
        t = self._size(x.left)
        if t > k:
            return self._select(k, x.left)
        elif t < k:
            return self._select(k-t-1, x.right)
        else:
            return x

    def _rank(self, k, x=None):
        """Return the rank of key `k` in the subtree rooted at `x`.

        .. note:: `rank` is the inverse of `select`."""
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
        x.N = self._size(x.left) + self._size(x.right) + 1
        return x

    def _delete_max(self, x=None):
        """Delete the maximum key in the subtree rooted at `x`."""
        if x.right is None:
            return x.left
        x.right = self._delete_max(x.right)
        x.N = self._size(x.left) + self._size(x.right) + 1
        return x

    def _delete(self, k, x=None):
        """Delete the node associated with `k` using eager Hibbard deletion."""
        if x is None:
            return
        # Update links and node counts as we go vs.:
        #   t = self.__getitem__(k, self._root)
        if k < x.key:
            x.left = self._delete(k, x.left)
        elif k > x.key:
            x.right = self._delete(k, x.right)
        else:
            if x.left is None:
                return x.right
            if x.right is None:
                return x.left
            t = x  # save pointer to Node to be deleted
            x = self._min(t.right)
            x.right = self._delete_min(t.right)
            x.left = t.left
        x.N = self._size(x.left) + self._size(x.right) + 1
        return x

    def _keys(self, lo, hi, x=None, q=None):
        """Recursively add keys to the given queue."""
        if x is None:
            return
        if q is None:
            q = Queue()
        if lo < x.key:
            self._keys(lo, hi, x.left, q)
        if lo <= x.key and hi >= x.key:
            q.enqueue(x.key)
        if hi > x.key:
            self._keys(lo, hi, x.right, q)
        return q


# -----------------------------------------------------------------------------
#         Test Functions
# -----------------------------------------------------------------------------
# TODO move to proper unit testing script
if __name__ == '__main__':
    import string
    import random

    tests = 0
    fails = 0

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

    # Test construction by dict
    random.seed(4206956)
    alphabet = [(c, i) for i, c in enumerate(string.ascii_uppercase)]
    random.shuffle(alphabet)

    td = BST(dict(alphabet))
    for k, v in alphabet:
        should_be(td[k], v)
    should_be(td.min(), 'A')
    should_be(td.max(), 'Z')

    # Test construction by list of tuples
    test_str = 'SORTEXAMPLE'
    test_set = set(test_str)
    data = [(c, i) for i, c in enumerate(test_str)]
    t = BST(data)

    # Tree looks like:
    #            S
    #           / \
    #         O    T
    #      /    \   \
    #     E      R   X
    #   /  \    /
    #  A    M  P
    #      /
    #     L
    
    should_be(len(t), len(test_set))  # test __len__

    for k, v in data:
        should_be(k in t, True)  # test __contains__

        # test __get__
        if k == 'E':
            should_be(t[k], max([v for k, v in data if k == 'E']))
        else:
            should_be(t[k], v)
    
    should_be(t.min(), 'A')
    should_be(t.max(), 'X')

    should_be(t.floor('O'), 'O')  # key in table
    should_be(t.ceil('O'),  'O')
    should_be(t.floor('Q'), 'P')  # key not in table
    should_be(t.ceil('Q'),  'R')
    should_be(t.floor(chr(ord('A') - 1)), None)  # char < t.min()
    should_be(t.ceil('Z'), None)                 # char > t.max()

    for i, c in enumerate(sorted(test_set)):
        should_be(t.select(i), c)
        should_be(t.rank(c), i)

    t.delete_min()  # remove 'A'
    should_be(t.min(), 'E')
    # Test updated ranks
    for i, c in enumerate(sorted(test_set - set('A'))):
        should_be(t.select(i), c)
        should_be(t.rank(c), i)

    t['A'] = 0  # replace value
    t.delete_max()
    should_be(t.max(), 'T')
    # Test updated ranks
    for i, c in enumerate(sorted(test_set - set('X'))):
        should_be(t.select(i), c)
        should_be(t.rank(c), i)

    t['X'] = 9  # replace value

    should_be(list(t.keys()), sorted(test_set))


    # Summary
    if fails > 0:
        print(f"{fails}/{tests} tests failed")
    else:
        print(f"All {tests} tests passed!")

# =============================================================================
# =============================================================================
