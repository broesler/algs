#!/usr/bin/env python3
# =============================================================================
#     File: reconstruct_bst.py
#  Created: 2021-03-01 17:17
#   Author: Bernie Roesler
# =============================================================================

"""Given a traversal of a BST, reconstruct the tree.
See: <https://algs4.cs.princeton.edu/32bst/> for more info.
"""

from algs.basics import Queue, Stack
from algs.search import BST


class BST(BST):
    """BST with classmethods to reconstruct the BST from traversal list."""

    class _NodeLimits:
        """Class to store the min/max allowable values of a given key."""

        def __init__(self, key, min=None, max=None):
            self.key = key
            self.min = min
            self.max = max

        def __str__(self):
            return f"{repr(self.key)}: {repr(self.min)}, {repr(self.max)}"

        def __repr__(self):
            return f"<{self.__class__.__name__}: {self.__str__()}>"

    @classmethod
    def from_pre_order(cls, pre_order=None, **kwargs):
        """Return True if input is a valid pre-order traversal of a BST."""
        st = cls(**kwargs)
        if pre_order is None:
            return st
        pre = Queue(pre_order)
        s = Stack()  # visited nodes
        st._root = st._Node(pre.dequeue())  # root is always first
        x = st._root  # pointer to location in tree
        s.push(x)
        root = None  # root of the current subtree
        while pre:
            k = pre.dequeue()
            if root is not None and k < root.key:
                raise KeyError(f"Key '{k}' is not in valide pre-order!")
            while s and s.peek().key < k:
                root = s.pop()  # update minimum key for this subtree
                x = root
            # Add child and move down the tree
            if k < x.key:
                x.left = st._Node(k)
                x = x.left
            elif k > x.key:
                x.right = st._Node(k)
                x = x.right
            else:
                raise KeyError(f"Key '{k}' is a duplicate!")
            s.push(x)
        # Fix sizes, heights, internal path lengths O(N lg N)
        st._update_nodes(st._root)
        return st

    @classmethod
    def from_level_order(cls, level_order=None, **kwargs):
        """Construct a BST given the level-order traversal of its keys.

        ..note:: This method does **not** update the size, height, or internal
            path length attributes. Instead, use the `height_r()`, or
            `internal_path_length_r()` methods to compute recursively.

        Raises
        ------
        KeyError
            If the given level-order is invalid.
        """
        st = cls(**kwargs)
        if level_order is None:
            return st
        lev = Queue(level_order)  # queue up the "nodes" to visit
        q = Queue()  # queue of _NodeLimits to visit (auxiliary to tree)
        r = Queue()  # queue of _Nodes to visit, parallel with q
        st._root = st._Node(lev.dequeue())  # root is first
        x = st._NodeLimits(st._root.key)  # pointer to _NodeLimits
        t = st._root  # pointer to _Nodes in actual tree
        q.enqueue(x)
        r.enqueue(t)
        while lev and q:
            x = q.dequeue()  # parent node
            t = r.dequeue()
            k = lev.peek()  # key in question
            # Check if next node can be left of x or not
            if k < x.key and (x.min is None or k > x.min):
                q.enqueue(st._NodeLimits(lev.dequeue(), x.min, x.key))
                t.left = st._Node(k)
                r.enqueue(t.left)
                k = lev.peek()
            # Check if next node can be right of x or not
            if k > x.key and (x.max is None or k < x.max):
                q.enqueue(st._NodeLimits(lev.dequeue(), x.key, x.max))
                t.right = st._Node(k)
                r.enqueue(t.right)

        # If we haven't used all of the keys, it is not a valid order
        if lev:
            raise KeyError('Invalid level-order!')

        # Fix sizes, heights, internal path lengths O(N lg N)
        st._update_nodes(st._root)
        return st

    def _update_nodes(self, x=None):
        """Iterate over the keys in post-order (depth-first)."""
        if x is None:
            return
        self._update_nodes(x.left)
        self._update_nodes(x.right)
        self._update_node(x)
        return


def is_pre_order(pre_order):
    """Return True if input is a valid pre-order traversal of a BST."""
    s = Stack()  # visited nodes
    min_key = None
    for k in pre_order:
        if min_key is not None and k < min_key:
            return False
        while s and s.peek() < k:
            min_key = s.pop()  # move right (increase minimum)
        s.push(k)  # move left
    return True


def is_level_order(level_order):
    """Return True if input is a valid level-order traversal of a BST."""
    pre = Queue(level_order)  # queue up the "nodes" to visit
    q = Queue()  # nodes to visit
    x = BST._NodeLimits(pre.dequeue())
    q.enqueue(x)
    while pre and q:
        x = q.dequeue()  # parent node
        k = pre.peek()  # key in question
        # Check if next node can be left of x or not
        if k < x.key and (x.min is None or k > x.min):
            q.enqueue(BST._NodeLimits(pre.dequeue(), x.min, x.key))
            k = pre.peek()
        # Check if next node can be right of x or not
        if k > x.key and (x.max is None or k < x.max):
            q.enqueue(BST._NodeLimits(pre.dequeue(), x.key, x.max))
    # If we haven't used all of the keys, it is not a valid order
    return False if pre else True


# -----------------------------------------------------------------------------
#         Test Client
# -----------------------------------------------------------------------------
def assert_orders(a, b):
    """Assert that BSTs `a` and `b` have the same node structure."""
    assert a == b
    assert a.pre_order() == b.pre_order()
    assert a.post_order() == b.post_order()
    assert a.level_order() == b.level_order()


# Test known example of pre-order traversal
st = BST.fromkeys(list('SEARCHEXAMPLE'))
assert st.pre_order() == list('SEACRHMLPX')  # compute manually
assert is_pre_order(st.pre_order())
assert not is_pre_order(list('SXEACRHMLP'))

# Test reconstructed examples
rst = BST.fromkeys(st.pre_order())  # O(N lg N) time
assert_orders(rst, st)

rst = BST.from_pre_order(st.pre_order())  # O(N) time
assert_orders(rst, st)

# Write class/function to test level-order traversal in O(N) time.
# Q: how do we determine if the input is *not* a level-order traversal?
st = BST.fromkeys(list('SEARCHEXAMPLE'))
rst = BST.fromkeys(st.level_order())  # gives correct tree, but O(N lg N) time
assert_orders(rst, st)

assert is_level_order(list('SEX'))
assert not is_level_order(list('SXE'))
assert is_level_order(list('SEXARCHMLP'))
assert not is_level_order(list('SEXRACHMLP'))

rst = BST.from_level_order(st.level_order())
assert_orders(rst, st)

# =============================================================================
# =============================================================================
