#!/usr/bin/env python3
# =============================================================================
#     File: draw_tree.py
#  Created: 2021-03-06 13:01
#   Author: Bernie Roesler
#
"""
  Description: Exercise 3.2.38 *Tree Drawing*
    Use instance variables to hold node coordinates, and use a recursive method
    to set the values of these variables.

    See <https://llimllib.github.io/pymag-trees/> for drawing algorithms.
"""
# =============================================================================

import random
import matplotlib.pyplot as plt

from algs.search import BST, RedBlackBST


class NodeArtist():
    """Wrapper class to add graphical coordinates to BST Nodes.

    ..note:: This class is a *recursive structure*! It builds itself by
        a pre-order traversal of the given BST.
    """
    def __init__(self, h=None, depth=0):
        if h is None:
            return
        self.x = 0          # set by layout methods
        self.y = 0
        self.mod = 0        # position modifier used by Weatherill
        self.depth = depth  # track depth independent of y-coordinate
        self.node = h       # pointer to node in BST
        self.left = NodeArtist(h.left, depth+1) or None
        self.right = NodeArtist(h.right, depth+1) or None

    # Slight trickery to set children to `None`: The constructor will construct
    # an object with no attributes if h is None, so instead of having to check
    # for attributes, or catching AttributeError, just redefine `__bool__`. The
    # constructor can then test if it returns a complete object or not to allow
    # client code to be both consistent with BST and more explicit than 
    # `if not h` `if h is None:` checks.
    def __bool__(self):
        return hasattr(self, 'x')  # no attributes set if None


class BSTArtist():
    """Class to plot a BST.

    Parameters
    ----------
    st : BST-like tree-structured symbol table
        `st` is assumed to have property `st._root`, and each node `x` is
        assumed to have property `x.left` and `x.right` for each of its
        children. The children are assumed to be `None` if empty.
    layout : str in {'knuth', ...}, optional
        string to declare the method of node layout when plotting.

    Attributes
    ----------
    fig, ax : :obj:Figure, :obj:Axis
        figure and axis handles to the plot.
    """
    def __init__(self, st, layout='knuth'):
        self.st = st  # pointer to the original BST
        self._root = NodeArtist(st._root)  # recursive structure!!
        self.fig = None
        self.ax = None
        self.set_layout(layout)

    @property
    def layout(self):
        return self.layout

    def get_layout(self):
        return self.layout

    # Write as "get/set" methods, since computing the layout could be as costly
    # as O(N^2). Make clear that it is a method call, not just a simple
    # property value.
    def set_layout(self, layout='knuth'):
        """Set the layout property and compute the node coordinates."""
        if layout == 'knuth':
            self._i = 0
            self._knuth_layout(self._root)
        elif layout == 'wetherell_naive':
            self._cols = [0] * self.st._root.height
            self._wetherell_naive_layout(self._root)
        elif layout == 'wetherell_3':
            self._cols = [0] * self.st._root.height
            self._mods = [0] * self.st._root.height
            self._wetherell_3_layout(self._root)
        elif layout == 'wetherell':
            self._cols = [0] * self.st._root.height
            self._mods = [0] * self.st._root.height
            self._wetherell_layout(self._root)
        else:
            raise ValueError(f"Invalid layout: {repr(layout)}")

    def _knuth_layout(self, h=None):
        """Set coordinates according to Knuth's method[1] of tree layout.

        Follows two principles:
            1. The edges of the tree should not cross each other.
            2. All nodes at the same height should be drawn on the same
               horizontal line to clarify the tree structure.

        The traversal is in-order, with the minimum key at the far left,
        increasing one step to the right for each subsequent key, regardless of
        height. Thus, each column may only be occupied by a single node.
        Knuth's layout leads to nicely ordered, but wide trees.

        .. [1] Knuth, Donald E. "Optimum Binary Search Trees".
            *Acta Informatica*, vol. 1, pp 14-25, 1971.

        Parameters
        ----------
        h : NodeArtist
            Root of the subtree to process
        i : float, optional
            x-coordinate of `h`
        """
        if h is None:
            return
        if h.left:
            self._knuth_layout(h.left)
        h.x = self._i
        h.y = -h.depth
        self._i += 1
        if h.right:
            self._knuth_layout(h.right)

    def _wetherell_naive_layout(self, h=None):
        """Use pre-order traversal by Wetherell and Shannon[1], Algorithm 1.

        This algorithm tracks the number of nodes on each level in `_cols`,
        incrementing in top-down fashion. The left-most node on the level
        starts at `x = 0`, with the rest of the level spreading to the right.
        This algorithm creates narrow trees, but parents are not centered above
        children.

        .. [1] Wetherell, Charles and Alfred Shannon. "Tidy Drawings of Trees".
            *IEEE Trans. Software Eng.*, vol. SE-5, pp 514-520, 1979.
        """
        if h is None:
            return
        i = h.depth
        h.x = self._cols[i]
        h.y = -i  # root at the top
        self._cols[i] += 1
        self._wetherell_naive_layout(h.left)
        self._wetherell_naive_layout(h.right)

    def _wetherell_3_layout(self, h=None):
        """Use pre-order traversal by Wetherell and Shannon[1], Algorithm 3.

        This method walks the tree twice:
            1. In post-order, assign preliminary x-coordinates. Also create
               a modifier for each node that will help to move sub-trees right.
            2. In pre-order, sum preliminary x-coordinate with modifiers of all
               parents.
        The y-coordinates are given by the heights (assumed pre-computed).

        .. [1] Wetherell, Charles and Alfred Shannon. "Tidy Drawings of Trees".
            *IEEE Trans. Software Eng.*, vol. SE-5, pp 514-520, 1979.
        """
        self._wetherell_first_pass(h)
        self._wetherell_second_pass(h)

    def _wetherell_layout(self, h=None):
        """Use pre-order traversal by Wetherell and Shannon[1], Algorithm 3.

        This method walks the tree twice:
            1. In post-order, assign preliminary x-coordinates. Also create
               a modifier for each node that will help to move sub-trees right.
            2. In pre-order, sum preliminary x-coordinate with modifiers of all
               parents.
        The y-coordinates are given by the heights (assumed pre-computed).

        .. [1] Wetherell, Charles and Alfred Shannon. "Tidy Drawings of Trees".
            *IEEE Trans. Software Eng.*, vol. SE-5, pp 514-520, 1979.
        """
        self._wetherell_first_pass(h)
        self._wetherell_mod_second_pass(h)

    def _wetherell_first_pass(self, h=None):
        """First, post-order pass of Wetherell Algorithm 3."""
        if h is None:
            return
        self._wetherell_first_pass(h.left)
        self._wetherell_first_pass(h.right)
        # Compute the preliminary x-positions and modifiers
        i = h.depth
        is_leaf = h.left is None and h.right is None
        if is_leaf:
            place = self._cols[i]
        elif h.left is None:
            place = h.right.x - 1
        elif h.right is None:
            place = h.left.x + 1
        else:
            place = (h.left.x + h.right.x) / 2  # centered over children
        # Modifiers remember the provisional place
        self._mods[i] = max(self._mods[i], self._cols[i] - place)
        # Actual position corrects h to the right to avoid siblings
        h.x = place if is_leaf else place + self._mods[i]
        h.y = -i
        self._cols[i] = h.x + 2
        h.mod = self._mods[i]

    def _wetherell_second_pass(self, h=None, mod_sum=0):
        """Second, pre-order pass of Wetherell Algorithm 3."""
        if h is None:
            return
        # Shift subtrees right by the cumulative modifiers of their parents
        h.x += mod_sum
        mod_sum += h.mod
        self._wetherell_second_pass(h.left, mod_sum)
        self._wetherell_second_pass(h.right, mod_sum)

    def _wetherell_mod_second_pass(self, h=None, mod_sum=0, p=None, from_right=False):
        """Second, in-order pass of Wetherell Algorithm 3."""
        if h is None:
            return
        # Shift subtrees right by the cumulative modifiers of their parents
        mod_sum += h.mod
        self._wetherell_mod_second_pass(h.left, mod_sum)
        # Compute positions in-order
        i = h.depth
        h.x = min(self._cols[i], h.x + mod_sum - h.mod)
        if h.left is not None:
            h.x = max(h.x, h.left.x + 1)
        # check whether we are in a right child
        if from_right:
            h.x = max(h.x, p.x + 1)
        # update arrays
        self._cols[i] = h.x + 2
        self._wetherell_mod_second_pass(h.right, mod_sum, p=h, from_right=True)

    def draw(self, fignum=None, layout=None, debug=False):
        """Plot the tree.

        Parameters
        ----------
        fignum : int, optional
            Figure number in which to draw. If a figure exists with the given
            `fignum`, it will be cleared. If `None`, a new Figure will be
            created.
        layout : str in {'knuth', 'wetherell_naive', 'wetherell_3'}, optional
            Choice of method to use for tree drawing.
        debug : bool, optional
            Enable extra plotting commands for debugging purposes.

        Returns
        -------
        fig, ax : Figure, Axis
            Handles to the Figure and Axis objects that hold the plot.
        """
        if layout:
            self.set_layout(layout)
        self.fig = plt.figure(fignum or 1, clear=True)
        self.ax = self.fig.add_subplot()
        self._draw(self._root)
        self.ax.set_aspect('equal')
        self.ax.autoscale_view()
        if not debug:
            self.ax.axis('off')
        plt.show()
        return self.fig, self.ax

    def _draw(self, h=None, ax=None):
        """Recursively plot the nodes and connectors to each child."""
        if h is None:
            return
        if ax is None:
            ax = self.ax
        self.draw_node(h, ax)
        self._draw(h.left, ax)
        self._draw(h.right, ax)

    def draw_node(self, h=None, null_links=True, ax=None, **kwargs):
        """Plot a single node and its children."""
        if h is None:
            return
        if ax is None:
            ax = self.ax

        NULL_DIST = 0.3

        # Plot the node itself
        circ = plt.Circle((h.x, h.y), radius=0.25, ec='k', fc='#EEE')
        ax.add_patch(circ)
        label = ax.annotate(h.node.key, xy=(h.x, h.y),
                            ha='center', va='center')

        # Plot lines to children
        # TODO
        #   * option to plot red links level with neighbors
        #   * plot next/prev of ThreadedST with curved, dashed arrows?
        if h.left:
            if self._is_red(h.left.node):
                color = 'C3'
                lw = 3
            else:
                color = 'k'
                lw = 2
            ax.plot((h.x, h.left.x), (h.y, h.left.y),
                    color=color, lw=lw, zorder=-1)
        elif null_links:
            ax.plot((h.x, h.x - NULL_DIST), (h.y, h.y - NULL_DIST), 'k', lw=2, zorder=-1)

        if h.right:
            if self._is_red(h.right.node):
                color = 'C3'
                lw = 3
            else:
                color = 'k'
                lw = 2
            ax.plot((h.x, h.right.x), (h.y, h.right.y),
                    color=color, lw=lw, zorder=-1)
        elif null_links:
            ax.plot((h.x, h.x + NULL_DIST), (h.y, h.y - NULL_DIST), 'k', lw=2, zorder=-1)

    def _is_red(self, h=None):
        """Return True if `h` is colored red. Calls RedBlackBST method unless
        we're drawing a regular BST.
        """
        try:
            return RedBlackBST._is_red(self.st, h)
        except AttributeError:
            return False


# -----------------------------------------------------------------------------
#         Test Client
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # st = BST.fromkeys(list('EASYQUESTION'))
    # st = RedBlackBST.fromkeys(list('EASYQUESTION'))

    # st = BST.fromkeys(sorted(list('SEARCHEXAMPLE')))  # in-order
    # st = BST.fromkeys(list('AXCSERHPL'))              # worst-case alternating
    # st = BST.fromkeys(list('SEARCHEXAMPLE'))            # arbitrary
    st = RedBlackBST.fromkeys(list('SEARCHEXAMPLE'))
    # st = BST.fromkeys(st.pre_order())  # test BST with shape of RedBlackBST

    layouts = dict({'knuth': 'Knuth',
                    'wetherell_naive': 'Wetherell and Shannon (naïve)',
                    'wetherell_3': 'Wetherell and Shannon (Algorithm 3)',
                    'wetherell': 'Wetherell and Shannon (complete)'})

    for i, (layout, title) in enumerate(layouts.items()):
        dt = BSTArtist(st)
        dt.draw(debug=True, fignum=i+1, layout=layout)
        dt.ax.set_title(title)


# =============================================================================
# =============================================================================
