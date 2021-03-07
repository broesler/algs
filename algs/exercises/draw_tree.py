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

import matplotlib.pyplot as plt

from algs.search import BST, RedBlackBST


class NodeArtist():
    """Wrapper class to add graphical coordinates to BST Nodes.
    
    ..note:: This class is a *recursive structure*! It builds itself by
        a pre-order traversal of the given BST.
    """
    def __init__(self, h=None):
        if h is None:
            return
        self.x = 0
        self.y = h.height
        self.node = h  # pointer to node in BST
        self.left = NodeArtist(h.left)
        self.right = NodeArtist(h.right)

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
        self.layout = layout

    @property
    def layout(self):
        return self.layout

    @layout.setter
    def layout(self, layout='knuth'):
        """Set the layout property and compute the node coordinates."""
        if layout == 'knuth':
            self._i = 0
            self._knuth_layout(self._root)
        elif layout == 'wetherell_naive':
            self._cols = [0] * self.st._root.height
            self._wetherell_naive_layout(self._root)
        else:
            raise ValueError(f"Invalid layout: {repr(layout)}")

    def _knuth_layout(self, h=None):
        """Set coordinates according to Knuth's method of tree layout.

        Follows two principles:
            1. The edges of the tree should not cross each other.
            2. All nodes at the same height should be drawn on the same
               horizontal line to clarify the tree structure.

        The traversal is in-order, with the minimum key at the far left,
        increasing one step to the right for each subsequent key, regardless of
        height. Knuth's layout leads to nicely ordered, but wide trees.

        Parameters
        ----------
        h : NodeArtist
            Root of the subtree to process
        i : float, optional
            x-coordinate of `h`
        """
        if not h:
            return
        if h.left:
            self._knuth_layout(h.left)
        h.x = self._i
        self._i += 1
        if h.right:
            self._knuth_layout(h.right)

    def _wetherell_naive_layout(self, h=None):
        """Use pre-order traversal (Wetherell and Shannon (1979)).
        
        This algorithm tracks the number of nodes on each level in `_cols`,
        incrementing in top-down fashion. The left-most node on the level
        starts at `x = 0`, with the rest of the level spreading to the right.
        This algorithm creates narrow trees, but parents are not centered above
        children.
        """
        if not h:
            return
        i = h.node.height-1
        h.x = self._cols[i]
        h.y = i
        self._cols[i] += 1
        self._wetherell_naive_layout(h.left)
        self._wetherell_naive_layout(h.right)

    def draw(self, debug=False, fignum=None, layout=None):
        """Plot the tree."""
        if layout:
            self.layout = layout
        self.fig = plt.figure(fignum or 1, clear=True)
        self.ax = self.fig.add_subplot()
        self._draw(self._root)
        self.ax.set_aspect('equal')
        self.ax.autoscale_view()
        self.ax.axis('off')
        plt.show()
        return self.fig, self.ax

    def _draw(self, h=None, ax=None):
        """Recursively plot the nodes and connectors to each child."""
        if not h:
            return
        if ax is None:
            ax = self.ax
        self.draw_node(h, ax)
        self._draw(h.left, ax)
        self._draw(h.right, ax)

    def draw_node(self, h=None, null_links=True, ax=None, **kwargs):
        """Plot a single node and its children."""
        if not h:
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
# st = BST.fromkeys(sorted(list('SEARCHEXAMPLE')))  # in-order
st = BST.fromkeys(list('AXCSERHPL'))                # worst-case alternating
# st = BST.fromkeys(list('SEARCHEXAMPLE'))
# st = RedBlackBST.fromkeys(list('SEARCHEXAMPLE'))

# st = BST.fromkeys(list('EASYQUESTION'))
# st = RedBlackBST.fromkeys(list('EASYQUESTION'))

dt = BSTArtist(st, layout='knuth')
dt.draw(fignum=1)
dt.ax.set_title('Knuth')

dt = BSTArtist(st, layout='wetherell_naive')
dt.draw(fignum=2)
dt.ax.set_title('Wetherell and Shannon (basic)')

# =============================================================================
# =============================================================================
