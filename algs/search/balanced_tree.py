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

import random

from algs.basics import Stack
from algs.search.tree import BST

__all__ = ['RedBlackBST', 'TopDown234', 'TopDown234_nr', 'TopDown234bothways',
           'BottomUp234', 'Unbalanced23', 'AVLTree']


class KeyChanged(Exception):
    pass


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
            self.Nred = int(self.color)  # 1 if red, 0 if black

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

            return (COLOR_SELF
                    + f"{{{repr(self.key)}: {repr(self.val)}}}"
                    + COLOR_END
                    + f", L:{left_str}, R:{right_str}")

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        self.Nrotations = 0  # track total rotations and splits to build tree
        self.Nsplits = 0
        super().__init__(*args, **kwargs)

    @property
    def Nred(self):
        """Return the number of red nodes in the tree."""
        return self._Nred(self._root)

    # Redefine put() operations to account for node colors
    def __setitem__(self, k, v):
        """Add a new node to subtree at `x`, associating `k` with `v`.
        If `k` is in subtree rooted at `x`, change its value to `v`."""
        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            self._cache.val = v
            return
        else:
            self._cost = 0  # Ex 3.3.43
            try:
                self._root = self._set(k, v, self._root)
                self._root.color = self._BLACK
                self._update_node(self._root)
            except KeyChanged:
                pass

    def __delitem__(self, k):
        """Delete the node associated with `k`.

        Raises
        ------
        KeyError
            If `k` is not in the table.
        """
        if not self.__contains__(k):
            raise KeyError(k)
        # If root is a 2-node, make it a 3-node
        if (not self._is_red(self._root.left) and
              not self._is_red(self._root.right)):
            self._root.color = self._RED
        self._root = self._delete(k, self._root)
        if self._CACHE_FLAG and self._cache and k == self._cache.key:
            self._cache = None

    def delete_min(self):
        """Delete the smallest key.

        Raises
        ------
        KeyError
            If the table is empty.
        """
        self._empty_check()
        # If root is a 2-node, make it a 3-node
        if (not self._is_red(self._root.left) and
              not self._is_red(self._root.right)):
            self._root.color = self._RED
        self._root = self._delete_min(self._root)
        if not self.is_empty:
            self._root.color = self._BLACK
        if self._CACHE_FLAG:
            self._cache = None

    def delete_max(self):
        """Delete the smallest key.

        Raises
        ------
        KeyError
            If the table is empty.
        """
        self._empty_check()
        # If root is a 2-node, make it a 3-node
        if (not self._is_red(self._root.right) and
              not self._is_red(self._root.left)):
            self._root.color = self._RED
        self._root = self._delete_max(self._root)
        if not self.is_empty:
            self._root.color = self._BLACK
        if self._CACHE_FLAG:
            self._cache = None

    # -------------------------------------------------------------------------
    #         Private API
    # -------------------------------------------------------------------------
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
            x = self._Node(k, v, color=self._RED)
            if self._CACHE_FLAG:
                self._cache = x
            return x

        # create a child, or update the value
        self._cost += 1
        if k < h.key:
            h.left = self._set(k, v, h.left)
        elif k > h.key:
            h.right = self._set(k, v, h.right)
        else:  # k == h.key
            h.val = v  # update the value
            if self._CACHE_FLAG:
                self._cache = h
            raise KeyChanged  # no need for rotations

        # Balance the tree (red links left-leaning)
        if self._is_red(h.right) and not self._is_red(h.left):
            h = self._rotate_left(h)
        if self._is_red(h.left) and self._is_red(h.left.left):
            h = self._rotate_right(h)
        # Split a 4-node into 3 2-nodes
        if self._is_red(h.right) and self._is_red(h.left):
            self._flip_colors(h)

        # Update node attributes
        self._update_node(h)
        return h

    def _delete(self, k, h=None):
        """Delete the item associated with `k` in the subtree rooted at `h`."""
        if k < h.key:
            # move left down the tree
            if not self._is_red(h.left) and not self._is_red(h.left.left):
                h = self._move_left(h)
            h.left = self._delete(k, h.left)
        else:
            # start on minimum key in the 3-node
            if self._is_red(h.left):
                h = self._rotate_right(h)
            if k == h.key and h.right is None:
                return
            # otherwise deal with right children
            if not self._is_red(h.right) and not self._is_red(h.right.left):
                h = self._move_right(h)
            if k == h.key:
                # Replace current node with its successor
                x = self._min(h.right)
                h.key = x.key
                h.val = x.val
                h.right = self._delete_min(h.right)
            else:
                h.right = self._delete(k, h.right)
        return self._balance(h)

    def _delete_min(self, h=None):
        """Delete the smallest key from the subtree rooted at `h`."""
        if h.left is None:
            return
        # If h.left is a 2-node, move a key from h.right to h.left
        if not self._is_red(h.left) and not self._is_red(h.left.left):
            h = self._move_left(h)
        h.left = self._delete_min(h.left)
        return self._balance(h)

    def _delete_max(self, h=None):
        """Delete the smallest key from the subtree rooted at `h`."""
        if self._is_red(h.left):
            h = self._rotate_right(h)
        if h.right is None:
            return
        # If h.right is a 2-node, move a key from h.left to h.right
        if not self._is_red(h.right) and not self._is_red(h.right.left):
            h = self._move_right(h)
        h.right = self._delete_max(h.right)
        return self._balance(h)

    # -------------------------------------------------------------------------
    #         Node Operations
    # -------------------------------------------------------------------------
    def _update_node(self, x):
        """Update the parameters of the node based on its subtree."""
        super()._update_node(x)
        x.Nred = int(x.color) + self._Nred(x.left) + self._Nred(x.right)

    def _Nred(self, x=None):
        """Return the number of red nodes in the subtree rooted at `x`."""
        return 0 if x is None else x.Nred

    def _is_red(self, x):
        """Return True if `x` is red, otherwise False."""
        return False if x is None else x.color == self._RED

    def _flip_colors(self, x):
        """Invert the colors of the `x` and its children."""
        x.color = not x.color
        x.left.color = not x.left.color
        x.right.color = not x.right.color
        # Update children before parent
        x.left.Nred = (int(x.left.color) +
                       self._Nred(x.left.left) +
                       self._Nred(x.left.right))
        x.right.Nred = (int(x.right.color) +
                        self._Nred(x.right.left) +
                        self._Nred(x.right.right))
        x.Nred = int(x.color) + self._Nred(x.left) + self._Nred(x.right)
        self.Nsplits += 1

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
        self.Nrotations += 1
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
        self.Nrotations += 1
        return x  # return the new parent

    def _move_left(self, h=None):
        """Move a key from the right child of `h` to its left child."""
        # Assuming that h is red and both h.left and h.left.left
        # are black, make h.left or one of its children red.
        self._flip_colors(h)
        if self._is_red(h.right.left):
            h.right = self._rotate_right(h.right)
            h = self._rotate_left(h)
        return h

    def _move_right(self, h=None):
        """Move a key from the left child of `h` to its right child."""
        # Assuming that h is red and both h.right and h.right.left
        # are black, make h.right or one of its children red.
        self._flip_colors(h)
        if self._is_red(h.left.left):
            h = self._rotate_right(h)
            self._flip_colors(h)
        return h

    def _balance(self, h=None):
        # Balance the tree (red links left-leaning)
        if self._is_red(h.right):
            h = self._rotate_left(h)
        if self._is_red(h.right) and not self._is_red(h.left):
            h = self._rotate_left(h)
        if self._is_red(h.left) and self._is_red(h.left.left):
            h = self._rotate_right(h)
        # Split a 4-node into 3 2-nodes
        if self._is_red(h.right) and self._is_red(h.left):
            self._flip_colors(h)
        self._update_node(h)
        return h

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
        if (self._is_red(h.right) or
              (self._is_red(h.left) and self._is_red(h.left.left))):
            return False
        else:
            return self._is23(h.left) and self._is23(h.right)

    def is_balanced(self):
        """Return True if all paths from the root to a null link have the same
        number of *black* links."""
        # Count black links to the minimum node
        black = 0
        x = self._root
        while x:
            if not self._is_red(x):
                black += 1
            x = x.left
        return self._is_balanced(self._root, black)

    def _is_balanced(self, h=None, black=0):
        """Return True if all paths from `h` to a null link have the same
        number of *black* links."""
        if h is None:
            return black == 0
        # Do not count red links
        if not self._is_red(h):
            black -= 1
        return (self._is_balanced(h.left, black) and
                self._is_balanced(h.right, black))


# Ex 3.3.23: 2-3 tree *without* balance restriction
class Unbalanced23(RedBlackBST):
    """Implements a 2-3 tree using the red-black representation, but without
    a balance requirement."""
    def _set(self, k, v, h=None, parent_is_3node=False):
        """Add a new node to subtree at `h`, associating `k` with `v`.
        If `k` is in subtree rooted at `h`, change its value to `v`.

        ..note:: `h` will always be `self._root` from the parent class.

        Parameters
        ----------
        k : key
            key for which to search
        v : value
            object to be associated with key `k`
        h : _Node, optional
            root of the subtree at which to begin search
        parent_is_3node : bool, optional
            True if the parent of the current node is a 3-node
        """
        # subtree is empty, create a new node with a red link to parent
        if h is None:
            if parent_is_3node:
                x = self._Node(k, v, color=self._BLACK)
            else:  # parent_is_2node
                x = self._Node(k, v, color=self._RED)
            if self._CACHE_FLAG:
                self._cache = x
            return x

        parent_is_3node = (self._is_red(h) or
                           self._is_red(h.left) or
                           self._is_red(h.right))

        # create a child, or update the value
        if k < h.key:
            h.left = self._set(k, v, h.left, parent_is_3node)
        elif k > h.key:
            h.right = self._set(k, v, h.right, parent_is_3node)
        else:  # k == h.key
            h.val = v  # update the value
            if self._CACHE_FLAG:
                self._cache = h
            raise KeyChanged  # no need for rotations

        # Update node attributes
        self._update_node(h)
        return h


# Ex 3.3.25 Top-down 2-3-4 Trees
class TopDown234(RedBlackBST):
    """Implements a top-down 2-3-4 tree using the red-black representation."""
    def _set(self, k, v, h=None):
        """Add a new node to subtree at `h`, associating `k` with `v`.
        If `k` is in subtree rooted at `h`, change its value to `v`.

        ..note:: `h` will always be `self._root` from the parent class.

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
            x = self._Node(k, v, color=self._RED)
            if self._CACHE_FLAG:
                self._cache = x
            return x

        # NOTE Only change from RedBlackBST is to move these lines from below
        # Split a 4-node into 3 2-nodes
        if self._is_red(h.right) and self._is_red(h.left):
            self._flip_colors(h)

        # create a child, or update the value
        if k < h.key:
            h.left = self._set(k, v, h.left)
        elif k > h.key:
            h.right = self._set(k, v, h.right)
        else:  # k == h.key
            h.val = v  # update the value
            if self._CACHE_FLAG:
                self._cache = h
            raise KeyChanged  # no need for rotations

        # Balance the tree (red links left-leaning)
        if self._is_red(h.right) and not self._is_red(h.left):
            h = self._rotate_left(h)
        if self._is_red(h.left) and self._is_red(h.left.left):
            h = self._rotate_right(h)

        # Update node attributes
        self._update_node(h)
        return h


# Ex 3.3.26 Top-down 2-3-4 Trees, non-recursively
class TopDown234_nr(RedBlackBST):
    """Implements a top-down 2-3-4 tree using the red-black representation, but
    sets elements with a single top-down pass."""
    def _set(self, k, v, h=None):
        """Add a new node to subtree at `h`, associating `k` with `v`.
        If `k` is in subtree rooted at `h`, change its value to `v`.

        ..note:: `h` will always be `self._root` from the parent class.

        Parameters
        ----------
        k : key
            key for which to search
        v : value
            object to be associated with key `k`
        h : _Node, optional
            root of the subtree at which to begin search
        """
        if self._root is None:
            self._root = self._Node(k, v, color=self._BLACK)
            if self._CACHE_FLAG:
                self._cache = self._root
            return self._root

        s = Stack()
        pp = p = None
        while h:
            if k == h.key:
                h.val = v
                if self._CACHE_FLAG:
                    self._cache = h
                raise KeyChanged  # no need for rotations
            else:
                # Split a 4-node into 3 2-nodes at the root
                if self._is_red(h.left) and self._is_red(h.right):
                    self._flip_colors(h)

                # NOTE do insertion *before* moving `h` so we retain both
                # parent pointers, otherwise we lose the grandparent
                s.push(h)
                if k < h.key:
                    if h.left is None:
                        # Make a 3-node or 4-node (depending on h.color)
                        h.left = self._Node(k, v, color=self._RED)
                        if self._CACHE_FLAG:
                            self._cache = h.left
                        if self._is_red(h):
                            h = self._rotate_right(p)
                            # Update the parent
                            if pp is None:
                                self._root = h
                            else:
                                if h.key < pp.key:
                                    pp.left = h
                                else:
                                    pp.right = h
                        break
                    else:
                        # Move down the tree
                        pp, p, h = self._balance_nr(pp, p, h, h.left)
                else:  # k > h.key
                    if h.right is None:
                        # Make a 3-node or 4-node
                        h.right = self._Node(k, v, color=self._RED)
                        if self._CACHE_FLAG:
                            self._cache = h.right
                        # Balance the tree (red links left-leaning)
                        if self._is_red(h.right) and not self._is_red(h.left):
                            h = self._rotate_left(h)
                            # Update the parent
                            if p is None:
                                self._root = h
                            else:
                                if h.key < p.key:
                                    p.left = h
                                else:
                                    p.right = h
                        if self._is_red(h) and self._is_red(h.left):
                            h = self._rotate_right(p)
                            # Update the parent
                            if pp is None:
                                self._root = h
                            else:
                                if h.key < pp.key:
                                    pp.left = h
                                else:
                                    pp.right = h
                        break
                    else:
                        # Move down the tree
                        pp, p, h = self._balance_nr(pp, p, h, h.right)

        # Update node counts and heights on path traveled back up the tree
        while s:
            x = s.pop()
            self._update_node(x)  # update N, height, internal path length

        return self._root

    def _balance_nr(self, pp, p, h, x):
        """Balanced the tree given `h`, one of its children `x`, parent `p`,
        and grandparent `pp`."""
        # Split a 4-node into 3 2-nodes before moving into the node
        if self._is_red(x.left) and self._is_red(x.right):
            self._flip_colors(x)
        # Rotate to balance the parent node
        if self._is_red(h.right) and not self._is_red(h.left):
            h = self._rotate_left(h)
            # Update the parent
            if p is None:
                self._root = h
            else:
                if h.key < p.key:
                    p.left = h
                else:
                    p.right = h
        if (p is not None and
                self._is_red(p.left) and self._is_red(p.left.left)):
            h = self._rotate_right(p)
            # Update the parent
            if pp is None:
                self._root = h
                p = None
            else:
                if h.key < pp.key:
                    pp.left = h
                else:
                    pp.right = h
        # Move down the tree
        pp = p
        p = h
        h = x
        return pp, p, h


# Ex 3.3.27 Top-down 2-3-4 Trees, with right-leaning links allowed
class TopDown234bothways(RedBlackBST):
    """Implements a top-down 2-3-4 tree using the red-black representation."""
    def _set(self, k, v, h=None):
        """Add a new node to subtree at `h`, associating `k` with `v`.
        If `k` is in subtree rooted at `h`, change its value to `v`.

        ..note:: `h` will always be `self._root` from the parent class.

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
            x = self._Node(k, v, color=self._RED)
            if self._CACHE_FLAG:
                self._cache = x
            return x

        # Split a 4-node into 3 2-nodes
        if self._is_red(h.right) and self._is_red(h.left):
            self._flip_colors(h)

        # create a child, or update the value
        if k < h.key:
            h.left = self._set(k, v, h.left)
        elif k > h.key:
            h.right = self._set(k, v, h.right)
        else:  # k == h.key
            h.val = v  # update the value
            if self._CACHE_FLAG:
                self._cache = h
            raise KeyChanged  # no need for rotations

        # Balance the tree (red links lean either way!)
        if self._is_red(h.right) and self._is_red(h.right.right):
            h = self._rotate_left(h)
        if self._is_red(h.left) and self._is_red(h.left.left):
            h = self._rotate_right(h)
        # NOTE new cases account for right-leaning links
        if self._is_red(h.right) and self._is_red(h.right.left):
            h.right = self._rotate_right(h.right)
            h = self._rotate_left(h)
        if self._is_red(h.left) and self._is_red(h.left.right):
            h.left = self._rotate_left(h.left)
            h = self._rotate_right(h)

        # Update node attributes
        self._update_node(h)
        return h


# Ex 3.3.28 Bottom-up 2-3-4 Tree
class BottomUp234(RedBlackBST):
    """Implements a bottom-up 2-3-4 tree using the red-black representation."""
    def _set(self, k, v, h=None):
        """Add a new node to subtree at `h`, associating `k` with `v`.
        If `k` is in subtree rooted at `h`, change its value to `v`.

        ..note:: `h` will always be `self._root` from the parent class.

        Parameters
        ----------
        k : key
            key for which to search
        v : value
            object to be associated with key `k`
        h : _Node, optional
            root of the subtree at which to begin search
        """
        if h is None:
            x = self._Node(k, v, color=self._RED)
            if self._CACHE_FLAG:
                self._cache = x
            return x

        # Split a 4-node into 3 2-nodes if it is a leaf
        if self._is_4node_leaf(h):
            self._flip_colors(h)

        if k < h.key:
            h.left = self._set(k, v, h.left)
        elif k > h.key:
            h.right = self._set(k, v, h.right)
        else:  # k == h.key
            h.val = v  # update the value
            if self._CACHE_FLAG:
                self._cache = h
            raise KeyChanged  # no need for rotations

        # Balance the tree (red links left-leaning)
        if self._is_red(h.right) and not self._is_red(h.left):
            h = self._rotate_left(h)
        if self._is_red(h.left) and self._is_red(h.left.left):
            # Split the 4-node if we have to
            if self._is_red(h.right):
                self._flip_colors(h)
            else:
                h = self._rotate_right(h)

        # Update node attributes
        self._update_node(h)
        return h

    def _is_4node_leaf(self, h=None):
        if (self._is_red(h.left) and
            self._is_red(h.right) and
            (h.left.left is None and
                h.left.right is None and
                h.right.left is None and
                h.right.right is None)):
            return True
        return False


class AVLTree(BST):
    """Implements an AVL height-balanced tree, without colors."""

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
            x = self._Node(k, v)
            if self._CACHE_FLAG:
                self._cache = x
            return x

        # create a child, or update the value
        self._cost += 1
        if k < h.key:
            h.left = self._set(k, v, h.left)
        elif k > h.key:
            h.right = self._set(k, v, h.right)
        else:  # k == h.key
            h.val = v  # update the value
            if self._CACHE_FLAG:
                self._cache = h
            return h
            # raise KeyChanged  # no need for rotations

        # Balance the tree based on height of children
        bal = self._height(h.left) - self._height(h.right)
        if bal < -1:  # right-heavy
            if k < h.right.key:   # new key was added to the left
                h.right = self._rotate_right(h.right)
                h = self._rotate_left(h)
            else:                 # new key was added to the right
                h = self._rotate_left(h)
        elif bal > 1:  # left-heavy
            if k < h.left.key:    # new key was added to the left
                h = self._rotate_right(h)
            else:                 # new key was added to the right
                h.left = self._rotate_left(h.left)
                h = self._rotate_right(h)

        # Update node height
        self._update_node(h)
        return h

    def _rotate_left(self, h):
        """Rotate node `h` such that its right child becomes its parent."""
        x = h.right
        h.right = x.left
        x.left = h
        self._update_node(h)  # update the new child before the new parent
        self._update_node(x)
        return x

    def _rotate_right(self, h):
        """Rotate node `h` such that its left child becomes its parent."""
        x = h.left
        h.left = x.right
        x.right = h
        self._update_node(h)  # update the new child before the new parent
        self._update_node(x)
        return x

    def is_height_balanced(self):
        """Return True if the heights of the subtrees rooted at each child
        differ by 1 or 0."""
        return self._is_height_balanced(self._root)

    def _is_height_balanced(self, x=None):
        if x is None:
            return True
        elif abs(self._height(x.left) - self._height(x.right)) > 1:
            return False
        else:
            return (self._is_height_balanced(x.left) and
                    self._is_height_balanced(x.right))


# Web Exercise: implement a Randomized Binary Search Tree
# TODO implement all methods for use in tests
class RandomizedBST(BST):
    """Implements a radomized BST per Martinez and Roura [0].

    .. [0]:: Martínez, Conrado and Roura, Salvador (1997). "Randomized binary
    search trees". *Journal of the ACM*, 45 (2): 288–323.
    """
    def _set(self, k, v, t=None):
        """Add a new node to subtree at `t`, associating `k` with `v`.
        If `k` is in subtree rooted at `t`, change its value to `v`.

        Parameters
        ----------
        k : key
            key for which to search
        v : value
            object to be associated with key `k`
        t : _Node, optional
            root of the subtree at which to begin search
        """
        # subtree is empty, create a new node with a red link to parent
        if t is None:
            new = self._Node(k, v)
            if self._CACHE_FLAG:
                self._cache = new
            return new

        # insert node here w.p. 1/(n+1)
        n = t.N
        r = random.randint(0, n)
        if r == n:
            return self._insert_at_root(k, v, t)
        elif k < t.key:
            t.left = self._set(k, v, t.left)
        else:  # k > t.key:
            t.right = self._set(k, v, t.right)

        return t

    def _insert_at_root(self, k, v, t=None):
        """Inset a new node at the root of the subtree of `t`.

        Parameters
        ----------
        k : key
            key to insert
        v : value
            object to be associated with key `k`
        t : _Node, optional
            root of the subtree at which to insert `k`
        """
        left, right = self._split(k, t)
        t = self._Node(k, v)
        t.left, t.right = left, right
        return t

    def _split(self, k, t=None, s=None, g=None):
        """Split the subtree rooted at `t` into `s` and `g`, where `s` contains
        all keys less than `k`, and `g` contains all keys greater than `k`."""
        if t is None:
            return None, None

        if k < t.key:
            g = t
            s, g.left = self._split(k, t.left, s, g.left)
        else:  # x > t.key
            s = t
            s.right, g = self._split(k, t.right, s.right, g)
        return s, g


# -----------------------------------------------------------------------------
#         Interactive test setup
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from algs.exercises.draw_tree import TreeArtist

    # EXPECT_STR = 'SEARCHXMPLJ'
    # EXPECT_STR = 'EASYQUESTION'
    # keys = list(EXPECT_STR)
    keys = [3, 7, 4, 9, 10, 0, 5, 6, 8, 2, 1, -8, -3, -5]

    # st = RedBlackBST.fromkeys(keys)
    # st = Unbalanced23.fromkeys(keys)
    # st = TopDown234.fromkeys(keys)
    # FIXME differs from recursive for 'SEARCHXMPL'. Root should be 4-node
    st = TopDown234_nr.fromkeys(keys)  
    # st = TopDown234bothways.fromkeys(keys)
    # st = BottomUp234.fromkeys(keys)
    # st = AVLTree.fromkeys(keys)
    # st = RandomizedBST.fromkeys(keys)
    TreeArtist(st).draw()
    assert st.isBST()
    assert st.is_balanced()
    # assert st.is_height_balanced()  # only AVL tree

    # # Compare two trees
    # tst = TopDown234.fromkeys(keys)
    # bst = BottomUp234.fromkeys(keys)
    # fig = plt.figure(1, clear=True)
    # gs = fig.add_gridspec(nrows=2, ncols=1)
    # ax1 = fig.add_subplot(gs[0])  # left side plot
    # ax2 = fig.add_subplot(gs[1])  # right side plot
    # ax1.set_title('Top-Down')
    # ax2.set_title('Bottom-Up')
    # TreeArtist(tst).draw(ax=ax1)
    # TreeArtist(bst).draw(ax=ax2)

# =============================================================================
# =============================================================================
