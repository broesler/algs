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

    # Add some color to the BST nodes!
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
                   + f"{{{repr(self.key)}: {repr(self.val)}}}, " \
                   + COLOR_END \
                   + f"L:{left_str}, R:{right_str}"

    # Redefine put() operations to account for node colors
    def __setitem__(self, k, v):
        """Add a new node to subtree at `x`, associating `k` with `v`.
        If `k` is in subtree rooted at `x`, change its value to `v`."""
        self._root = self._set(k, v, self._root)
        self._root.color = self._BLACK

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
        # subtree is empty, create a new node with a red link to parent
        if x is None:
            return self._Node(k, v, color=self._RED)

        # create a child, or update the value
        if k < x.key:
            x.left = self._set(k, v, x.left)
        elif k > x.key:
            x.right = self._set(k, v, x.right)
        else:  # k == x.key
            x.val = v  # update the value

        # Update the colors (i.e. split a 4-node)
        if self._is_red(x.right) and not self._is_red(x.left):
            x = self._rotate_left(x)
        if self._is_red(x.left) and self._is_red(x.left.left):
            x = self._rotate_right(x)
        if self._is_red(x.right) and self._is_red(x.left):
            self._flip_colors(x)

        self._update_node(x)
        return x

    def _rotate_left(self, h):
        """Rotate node `h` such that its right child becomes its parent."""
        x = h.right
        h.right, x.left = x.left, h
        x.color = h.color
        h.color = self._RED
        x.N = h.N
        self._update_node(h)
        return x  # return the new parent

    def _rotate_right(self, h):
        """Rotate node `h` such that its left child becomes its parent."""
        x = h.left
        h.left, x.right = x.right, h
        x.color = h.color
        h.color = self._RED
        x.N = h.N
        self._update_node(h)
        return x  # return the new parent

    def _is_red(self, x):
        """Return True if `x` is red, otherwise False."""
        return False if x is None else x.color == self._RED

    def _flip_colors(self, x):
        """Convert two red children to black, and parent to red."""
        x.color = self._RED
        x.left.color = self._BLACK
        x.right.color = self._BLACK

# =============================================================================
# =============================================================================
