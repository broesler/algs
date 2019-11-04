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
    """
    def __init__(self, items=list()):
        self._items = list()
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
    def __setitem__(self, k, v):
        """Insert a new value `v` associated with key `k`.
        If `k` is in the table, change its value to `v`."""
        self.__delitem__(k)
        self._items.append((k, v))

    def __getitem__(self, k):
        """Return the value associated with the given `k`."""
        for key, val in self._items:
            if k == key:
                return val
        else:
            raise KeyError(k)

    def __contains__(self, k):
        """Return True if `k` is present in the table, False otherwise."""
        for key, val in self._items:
            if k == key:
                return True
        else:
            return False

    def __delitem__(self, k):
        """Delete the item associated with `k`."""
        for i, (key, val) in enumerate(self._items):
            if k == key:
                del self._items[i]
                break

    def keys(self):
        """Return an iterator of all of the keys in the table."""
        return iter([k for k, v in self._items])

    def __iter__(self):
        """Return an iterator of all of the keys in the table."""
        yield from self.keys()



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

    # TODO make `dict_keys`-like class to create view of keys?
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

    def select(self, r):
        """Return the key of rank `r`."""
        return self._select(r, self._root).key

    def delete_min(self):
        """Delete the smallest key."""
        self._root = self._delete_min(self._root)

    def delete_max(self):
        """Delete the largest key."""
        self._root = self._delete_max(self._root)

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
    keys.__doc__ = docstring.format(rtype='keys')

    def values(self, lo=None, hi=None):
        func = self._make_inorder_iterator(rtype='values')
        return func(self, lo, hi)
    values.__doc__ = docstring.format(rtype='values')

    def items(self, lo=None, hi=None):
        func = self._make_inorder_iterator(rtype='items')
        return func(self, lo, hi)
    items.__doc__ = docstring.format(rtype='items')

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
    def _size(self, x=None):
        """Return the size of the subtree rooted at Node `x`."""
        if x is None:
            return 0
        else:
            return x.N

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

        .. note:: `select` is the inverse of `rank`."""
        if x is None:
            raise KeyError(r)
        t = self._size(x.left)
        if t > r:
            return self._select(r, x.left)
        elif t < r:
            return self._select(r-t-1, x.right)
        else:
            return x

    def _rank(self, k, x=None):
        """Return the rank of key `k` in the subtree rooted at `x`.

        .. note:: `rank` is the inverse of `select`."""
        if x is None:
            raise KeyError(k)
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

    # factory for generic in-order iteration over keys
    def _make_inorder_iterator(self, rtype):
        """Create an iterator over the desired type."""
        def iterator(self, lo=None, hi=None):
            if lo is None:
                lo = self.min()
            if hi is None:
                hi = self.max()
            q = self._iterate(lo, hi, x=self._root, rtype=rtype)
            return iter(q)
        return iterator

    def _iterate(self, lo, hi, x=None, q=None, rtype='keys'):
        """Recursively add items to the given queue."""
        # Defaults
        if x is None:
            return
        if q is None:
            q = Queue()
        # Enqueue by key order
        if lo < x.key:
            self._iterate(lo, hi, x.left, q, rtype)
        if lo <= x.key and hi >= x.key:
            q.enqueue(x.key if rtype == 'keys' else (x.val if rtype == 'values' else (x.key, x.val)))
        if hi > x.key:
            self._iterate(lo, hi, x.right, q, rtype)
        return q

    def _level_order(self):
        """Return an iterator over the keys in level-order (breadth-first)."""
        keys = Queue()
        q = Queue()
        q.enqueue(self._root)
        while q:
            x = q.dequeue()
            if x is None:
                continue
            keys.enqueue(x.key)
            q.enqueue(x.left)
            q.enqueue(x.right)
        return iter(keys)


# -----------------------------------------------------------------------------
#         Test Functions
# -----------------------------------------------------------------------------
# TODO move to proper unit testing script
if __name__ == '__main__':
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

    test_str = 'SEARCHEXAMPLE'
    test_set = set(test_str)
    data = [(c, i) for i, c in enumerate(test_str)]

    # should_be(SequentialSearchST().is_empty, True)
    should_be(BST().is_empty, True)

    # #---------- Test SequentialSearchST ----------
    # t = SequentialSearchST(data)
    # for k, v in data:
    #     if k == 'E' or k == 'A':
    #         should_be(t[k], max([v for key, v in data if key == k]))
    #     else:
    #         should_be(t[k], v)
    #
    # # t.keys() not guaranteed in order
    # should_be(sorted(t.keys()), sorted(test_set))
    # should_be((t.keys() == sorted(test_set)), False)
    #
    # del t['A']
    # should_be(sorted(t.keys()), sorted(test_set - set('A')))
    #

    #---------- Test BST ----------
    # Test bad input type
    try:
        t = BST(list('EXAMPLE'))
    except ValueError:
        should_be(True, True)
    else:
        should_be(True, False)

    # Test construction by list of tuples
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

    for i, c in enumerate(sorted(test_set)):
        should_be(t.select(i), c)
        should_be(t.rank(c), i)

    # Level-order traversal
    should_be(list(t._level_order()), list('SEXARCHMLP'))

    # In-order traversal
    should_be(list(t.keys()), sorted(test_set))
    should_be(list(t.keys(lo='P')), list('PRSX'))
    should_be(list(t.keys('F', 'Q')), list('HLMP'))  # subset of keys
    should_be(list(t.keys(hi='P')), list('ACEHLMP'))

    data_set = data.copy()
    data_set.remove(('E', 1))
    data_set.remove(('A', 2))
    data_set.remove(('E', 6))
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
    try:
        t['E']
    except KeyError:
        should_be(True, True)   # pass if we get a KeyError as expected
    else:
        should_be(True, False)  # fail if we didn't actually delete the key!
    t['E'] = v

    # delete the root
    v = t['S']
    del t['S']
    should_be(t._root.key, 'X')
    t['S'] = v

    # Summary
    if fails > 0:
        print(f"{fails}/{tests} tests failed")
    else:
        print(f"All {tests} tests passed!")

# =============================================================================
# =============================================================================
