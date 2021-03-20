#!/usr/bin/env python3
# =============================================================================
#     File: balanced_tree.py
#  Created: 2021-03-05 23:21
#   Author: Bernie Roesler
#
"""
  Description: Balanced Search Trees.
"""
# =============================================================================

from algs.basics import Queue as _Queue
from algs.search import BST

__all__ = ['RedBlackBST']

# TODO put parameters and attributes into general string and set the doc.


class RedBlackBST(BST):
    """Implements a red-black binary search tree.

    ..note:: A red-black tree is a 1-1 map to a 2-3 tree.

    Parameters
    ----------
    items : mapping, dict-like
        Iterable of (key, value) tuples to be put onto the tree.

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
    # Define internal boolean constants for color of edge
    _RED = True
    _BLACK = False

    class _Node(BST._Node):
        """Internal RedBlack Node. Same as BST node but add color."""
        def __init__(self, *args, color=None, **kwargs):
            super().__init__(*args, **kwargs)
            self.color = color

        def __str__(self):
            # Print the nodes with colors!
            COLOR_RED = '\033[31m'
            COLOR_END = '\033[0m'
            COLOR_SELF = COLOR_RED if self.color else COLOR_END

            # Avoid recursion through entire tree!! Just print each child
            if self.left:
                COLOR_LEFT = COLOR_RED if self.left.color else COLOR_END
                left_str = (COLOR_LEFT
                           + f"{{{repr(self.left.key)}: {repr(self.left.val)}}}"
                           + COLOR_END)
            else:
                left_str = 'None'

            if self.right:
                COLOR_RIGHT = COLOR_RED if self.right.color else COLOR_END
                right_str = (COLOR_RIGHT
                            + f"{{{repr(self.right.key)}: {repr(self.right.val)}}}"
                            + COLOR_END)
            else:
                right_str = 'None'

            return COLOR_SELF \
                   + f"{{{repr(self.key)}: {repr(self.val)}}}" \
                   + COLOR_END \
                   + f", L:{left_str}, R:{right_str}"

    # Redefine put() operations to account for node colors
    def __setitem__(self, k, v):
        """Add a new node to subtree at `x`, associating `k` with `v`.
        If `k` is in subtree rooted at `x`, change its value to `v`."""
        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            self._cache.val = v
            return
        else:
            self._root = self._set(k, v, self._root)
            self._root.color = self._BLACK

    def _set(self, k, v, h=None):
        """Add a new node to subtree at `h`, associating `k` with `v`.
        If `k` is in subtree rooted at `h`, change its value to `v`.

        Parameters
        ----------
        k : key
            key for which to search
        v : value
            object to be associated with key `k`
        h : _Node, optional
            root of the subtree at which to begin search
        """
        # subtree is empty, create a new node with a red link to parent
        if h is None:
            return self._Node(k, v, color=self._RED)

        # create a child, or update the value
        if k < h.key:
            h.left = self._set(k, v, h.left)
        elif k > h.key:
            h.right = self._set(k, v, h.right)
        else:  # k == h.key
            h.val = v  # update the value
            return h   # no noeed for rotations if we only change value

        # Rotate red links to be left-leaning (i.e. split a 4-node)
        if self._is_red(h.right) and not self._is_red(h.left):
            h = self._rotate_left(h)
        if self._is_red(h.left) and self._is_red(h.left.left):
            h = self._rotate_right(h)
        if self._is_red(h.right) and self._is_red(h.left):
            self._flip_colors(h)

        # Update node attributes
        self._update_node(h)
        # In 2-3 tree analogue, red nodes are at same height as their parent,
        # so adjust the height, and reduce internal path length accordingly
        # if self._is_red(h.left):
        #     h.height = 1 + max(self._height(h.left) - 1, self._height(h.right))
        #     h.ipl = self._internal_path_length(h.left) \
        #             + self._internal_path_length(h.right) + self._size(h.right)
        return h

    def _rotate_left(self, h):
        """Rotate node `h` such that its right child becomes its parent."""
        assert h is not None and self._is_red(h.right)
        x = h.right
        h.right = x.left
        x.left = h
        x.color = h.color
        h.color = self._RED
        # Update the new child before the new parent
        self._update_node(h)
        self._update_node(x)
        return x  # return the new parent

    def _rotate_right(self, h):
        """Rotate node `h` such that its left child becomes its parent."""
        assert h is not None and self._is_red(h.left)
        x = h.left
        h.left = x.right
        x.right = h
        x.color = h.color
        h.color = self._RED
        # Update the new child before the new parent
        self._update_node(h)
        self._update_node(x)
        return x  # return the new parent

    def _flip_colors(self, x):
        """Convert two red children to black, and parent to red."""
        x.color = self._RED
        x.left.color = self._BLACK
        x.right.color = self._BLACK

    def _is_red(self, x):
        """Return True if `x` is red, otherwise False."""
        return False if x is None else x.color == self._RED

    # -------------------------------------------------------------------------
    #         Certification
    # -------------------------------------------------------------------------
    def isRedBlackBST(self):
        """Return True if all of the red-black BST properties hold."""
        return self.isBST() and self.is23() and self.is_balanced()

    def is23(self):
        """Return True if no node is connected to two red links, and there are
        no right-leaning red links."""
        return self._is23(self._root)

    def _is23(self, h=None):
        if h is None:
            return True
        if self._is_red(h.right):
            return False
        elif self._is_red(h.left) and self._is_red(h.left.left):
            return False
        else:
            return self._is23(h.left) and self._is23(h.right)

    def is_balanced(self):
        """Return True if all paths from the root to a null link have the same
        number of *black* links."""
        lens = self._null_path_lengths(self._root, depth=0)
        return all([x == lens.peek() for x in lens])

    def _null_path_lengths(self, h=None, q=None, depth=0):
        """Return a list of path lengths to all null links."""
        if h is None:
            return
        if q is None:
            q = _Queue()
        if h.left is None or h.right is None:
            q.enqueue(depth)
        # Do not count red links
        new_depth = depth if self._is_red(h.left) else depth + 1
        self._null_path_lengths(h.left, q, new_depth)
        self._null_path_lengths(h.right, q, depth + 1)
        return q


# Interactive test setup
if __name__ == '__main__':
    EXPECT_STR = 'SEARCHEXAMPLE'
    data = list((c, i) for i, c in enumerate(EXPECT_STR))
    st = RedBlackBST(data)
    # FIXME root is not black? or str() does not work at root

# =============================================================================
# =============================================================================
