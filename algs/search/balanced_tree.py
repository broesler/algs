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

from algs.basics import Stack as _Stack
from algs.search.tree import _empty_check, BST

__all__ = ['RedBlackBST', 'TopDown234', 'BottomUp234', 'Unbalanced23']


class KeyChangeException(Exception):
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
            self._cost = 0  # Ex 3.2.44
            try:
                self._root = self._set(k, v, self._root)
                self._root.color = self._BLACK
                self._update_node(self._root)
            except KeyChangeException:
                pass

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
            raise KeyChangeException  # no need for rotations

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
        _empty_check(self)
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
        _empty_check(self)
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
        if self._is_red(h.right):
            return False
        elif self._is_red(h.left) and self._is_red(h.left.left):
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

        parent_is_3node = (True if (self._is_red(h) or
                                     self._is_red(h.left) or
                                     self._is_red(h.right))
                           else False)

        # create a child, or update the value
        if k < h.key:
            h.left = self._set(k, v, h.left, parent_is_3node)
        elif k > h.key:
            h.right = self._set(k, v, h.right, parent_is_3node)
        else:  # k == h.key
            h.val = v  # update the value
            if self._CACHE_FLAG:
                self._cache = h
            raise KeyChangeException  # no need for rotations

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
            raise KeyChangeException  # no need for rotations

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
        s = _Stack()
        p = self._root
        while h:
            if k == h.key:
                h.val = v
                if self._CACHE_FLAG:
                    self._cache = h
                raise KeyChangeException  # no need for rotations
            else:
                # Split a 4-node into 3 2-nodes
                if (not self._is_red(h) and
                        self._is_red(h.left) and
                        self._is_red(h.right)):
                    self._flip_colors(h)
                s.push(h)
                if k < h.key:
                    x = h.left  # potential path
                    if x is None:
                        # Make a 3-node or 4-node (depending on h.color)
                        h.left = self._Node(k, v, color=self._RED)
                        # Balance the tree (red links left-leaning)
                        if self._is_red(h.right) and not self._is_red(h.left):
                            h = self._rotate_left(h)
                        if self._is_red(h.left) and self._is_red(h.left.left):
                            h = self._rotate_right(h)
                        if self._root is h.right or self._root is h.left:
                            self._root = h
                        break
                    else:
                        p = h
                        h = h.left
                else:  # k > h.key
                    x = h.right
                    if x is None:
                        # Make a 3-node or 4-node
                        h.right = self._Node(k, v, color=self._RED)
                        # Balance the tree (red links left-leaning)
                        if self._is_red(h.right) and not self._is_red(h.left):
                            h = self._rotate_left(h)
                        # if self._is_red(h.left) and self._is_red(h.left.left):
                        #     h = self._rotate_right(h)
                        if self._is_red(h) and self._is_red(h.left):
                            p.left = h
                            p = self._rotate_right(p)
                        # TODO HOOK INTO P AT THE BOTTOM
                        if self._root is h.right or self._root is h.left:
                            self._root = h
                        break
                    else:
                        p = h
                        h = h.right

        if self._root is None:
            self._root = self._Node(k, v, color=self._BLACK)

        # Update node counts and heights on path traveled back up the tree
        while s:
            x = s.pop()
            self._update_node(x)  # update N, height, internal path length

        return self._root


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
            raise KeyChangeException  # no need for rotations

        # Split a 4-node into 3 2-nodes
        if self._is_red(h.left) and self._is_red(h.right):
            self._flip_colors(h)
        # Balance the tree (red links left-leaning)
        if self._is_red(h.right) and not self._is_red(h.left):
            h = self._rotate_left(h)
        if self._is_red(h.left) and self._is_red(h.left.left):
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


# -----------------------------------------------------------------------------
#         Interactive test setup
# -----------------------------------------------------------------------------
# if __name__ == '__main__':
    # import matplotlib.pyplot as plt
    # from algs.exercises.draw_tree import TreeArtist
    # EXPECT_STR = 'SEARCHEXAMPLE'
    # # EXPECT_STR = 'EASYQUESTION'
    # data = list((c, i) for i, c in enumerate(EXPECT_STR))
    # st = RedBlackBST(data)
    # st = TopDown234(data)
    # st = TopDown234_nr(data)
    # st = Unbalanced23(data)
    # st = BottomUp234(data)
    # keys = [3, 7, 4, 9, 10, 0, 5, 6, 8, 2, 1]
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
