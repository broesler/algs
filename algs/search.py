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
    >>> t = BST()
    >>> t['A'] = 0
    >>> t['B'] = 1
    >>> t['C'] = 2
    >>> t['A'] = 10
    >>> t.min() == 'A'
    True
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
                self._root = self._put(k, v, self._root)
            return
        except AttributeError:
            pass 

        # List of tuples construction
        try:
            for v in items:
                self._root = self._put(v[0], v[1], self._root)
            return
        except IndexError:
            raise Exception('Input format not supported!')

    @property
    def size(self):
        return self._size(self._root)

    @property
    def is_empty(self):
        return self._size == 0

    def min(self):
        """Return the minimum key in the tree."""
        return self._min(self._root).key

    def max(self):
        """Return the maximum key in the tree."""
        return self._max(self._root).key

    def floor(self, key):
        """Return the largest key less than or equal tothe given `key`."""
        pass

    def ceil(self, key):
        """Return the smallest key greater than or equal to the given `key`."""
        pass

    def rank(key):
        """Return the number of keys less than given `key`."""
        pass

    def select(self, k):
        """Return the key of rank `k`."""
        pass

    def delete_min(self):
        """Delete the smallest key."""
        pass

    def delete_max(self):
        """Delete the largest key."""
        pass

    # ------------------------------------------------------------------------- 
    #         Private API
    # -------------------------------------------------------------------------
    def _size(self, root=None):
        """Return the size of the subtree located at `root`."""
        if root is None:
            return 0
        else:
            return root.N

    def _get(self, k, x=None):
        """Return the value associated with the given `k`.

        Parameters
        ----------
        k : key
            key for which to search
        x : _Node, optional
            root of the subtree at which to begin search
        """
        # got to the bottom of the tree, key not found
        if x is None:
            return None

        if k < x.key:
            return self._get(k, x.left)
        elif k > x.key:
            return self._get(k, x.right)
        else:  # k == root.key!
            return x.val

    def _put(self, k, v, x=None):
        """Add a new node to subtree at `x`, associating `k` with `v`. 
        If `k` is in subtree rooted at `x`, change its value to `v`."""
        # subtree is empty, create a new node
        if x is None:
            return self._Node(k, v)

        # create a child, or update the value
        if k < x.key:
            x.left = self._put(k, v, x.left)
        elif k > x.key:
            x.right = self._put(k, v, x.right)
        else:  # k == x.key
            x.val = v  # update the value

        # Update the size of the subtree located at the given root
        x.N = self._size(x.left) + self._size(x.right) + 1
        return x

    def _min(self, x=None):
        """Return the minimum key in the subtree rooted at `x`."""
        return x if x.left is None else self._min(x.left)

    def _max(self, x=None):
        return x if x.right is None else self._max(x.right)
    
    # -------------------------------------------------------------------------
    #         Object Methods
    # -------------------------------------------------------------------------
    def __getitem__(self, k):
        """Return the value associated with the given `k`."""
        return self._get(k, self._root)

    def __setitem__(self, k, v):
        """Insert a new `k`-`v` pair into the tree."""
        self._root = self._put(k, v, self._root)

    def __delitem__(self, k):
        """Delete the node associated with `k`."""
        pass

    def __contains__(self, k):
        """Return True if `k` is present in the tree, False otherwise."""
        pass

    def __str__(self):
        return str(self._root)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"


# ----------------------------------------------------------------------------- 
#         Test Functions
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import string
    import random

    tests = 0
    fails = 0

    def should_be(a, b):
        """Test a condition."""
        global tests, fails
        tests += 1
        try:
            assert a == b
        except AssertionError as e:
            fails += 1
            print(f"[{test_name}]: Got: {a}, Expected: {b}")
            # raise e

    # Test construction by list of tuples
    test_name = 'SORTEXAMPLE'
    t = BST([(c, i) for i, c in enumerate('SORTEXAMPLE')])
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
    #
    should_be((t._root.key, t._root.val),                                            ( 'S',  0))
    should_be((t._root.left.key, t._root.left.val),                                  ( 'O',  1))
    should_be((t._root.left.right.key, t._root.left.right.val),                      ( 'R',  2))
    should_be((t._root.right.key, t._root.right.val),                                ( 'T',  3))
    should_be((t._root.left.left.key, t._root.left.left.val),                        ( 'E', 10))  # 'E' is updated at end
    should_be((t._root.right.right.key, t._root.right.right.val),                    ( 'X',  5))
    should_be((t._root.left.left.left.key, t._root.left.left.left.val),              ( 'A',  6))
    should_be((t._root.left.left.right.key, t._root.left.left.right.val),            ( 'M',  7))
    should_be((t._root.left.right.left.key, t._root.left.right.left.val),            ( 'P',  8))
    should_be((t._root.left.left.right.left.key, t._root.left.left.right.left.val),  ( 'L',  9))

    should_be(t.min(), 'A')
    should_be(t.max(), 'X')

    # Test construction by dict
    test_name = 'Alphabet'
    random.seed(4206956)
    data = [(c, i) for i, c in enumerate(string.ascii_uppercase)]
    random.shuffle(data)

    td = BST(dict(data))
    should_be(td.min(), 'A')
    should_be(td.max(), 'Z')

    # Summary
    if fails > 0:
        print(f"{fails}/{tests} tests failed")
    else:
        print(f"All {tests} tests passed!")

# =============================================================================
# =============================================================================
