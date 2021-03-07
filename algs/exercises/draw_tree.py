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
    ???
    """
    def __init__(self, st, layout='knuth'):
        self.st = st  # pointer to the original BST
        self._root = NodeArtist(st._root)  # recursive structure!!
        self.fig = None
        self.ax = None
        if layout == 'knuth':
            self.layout = layout
            self._knuth_layout(self._root)
        else:
            raise ValueError(f"Invalid layout: {repr(layout)}")

    def _knuth_layout(self, h=None, i=0, depth=0):
        """Set coordinates according to Knuth's method of tree layout.

        Follows two principles:
            1. The edges of the tree should not cross each other.
            2. All nodes at the same depth should be drawn on the same
               horizontal line to clarify the tree structure.

        Parameters
        ----------
        h : NodeArtist
            Root of the subtree to process
        i : float, optional
            x-coordinate of `h`
        depth : float, optional
            y-coordinate of `h`
        """
        if h is None:
            return
        if h.left:
            self._knuth_layout(h.left, i-1)
        h.x = i
        if h.right:
            self._knuth_layout(h.right, i+1)

    def draw(self, debug=False):
        """Plot the tree."""
        self.fig = plt.figure(1, clear=True)
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
        # Plot the node itself
        circ = plt.Circle((h.x, h.y), radius=0.2, ec='k', fc='#EEE')
        ax.add_patch(circ)
        label = ax.annotate(h.node.key, xy=(h.x, h.y), 
                            ha='center', va='center')
        # Plot lines to children
        if h.left:
            ax.plot((h.x, h.left.x), (h.y, h.left.y), 'k', lw=2, zorder=-1)
        if h.right:
            ax.plot((h.x, h.right.x), (h.y, h.right.y), 'k', lw=2, zorder=-1)




st = BST.fromkeys(list('SEARCHEXAMPLE'))
# st = BST.fromkeys(list('SEX'))
dt = BSTArtist(st)
dt.draw(debug=True)

# =============================================================================
# =============================================================================
