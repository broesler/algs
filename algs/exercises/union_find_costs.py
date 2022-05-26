#!/usr/bin/env python3
# =============================================================================
#     File: union_find_costs.py
#  Created: 2022-05-25 19:36
#   Author: Bernie Roesler
#
"""
Amortized cost plots of the union-find datatypes.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from algs.unionfind import (read_uf_file, QuickFindUF, QuickUnionUF,
                            WeightedQuickUnionUF, WeightedQuickFindUF)


def cost_plot(oc, ax=None, y_max=0):
    """Plot amortized costs.

    Parameters
    ----------
    oc : :obj:OpsCounter
        Container class with arrays of operation costs.
    ax : Axes, optional
        If None, `ax = plt.gca()`.
    y_max : float, optional
        Maximum value for the y-axis.

    Returns
    -------
    ax : Axes
        The axes in which the plot was made.
    """
    ax.scatter(oc.ops, oc.cost, color=0.7*np.r_[1, 1, 1], s=1, alpha=0.8)
    ax.scatter(oc.ops, oc.tots, c='C3', s=1, alpha=0.8)

    # Label the final average total cost value
    ax.annotate(rf"{oc.tots[-1]:.0f}",
                xy=(oc.M, oc.tots[-1]), xycoords='data',
                xytext=(1.1*oc.M, 1.1*oc.tots[-1]), textcoords='data',
                ha='center', va='bottom', color='C3',
                arrowprops=dict(arrowstyle="-|>", color="C3"))

    ax.set_title(title, color='C3', fontweight='bold', fontsize=9, 
                 x=-0.1, ha='left', pad=10, va='bottom')

    ax.set_xlim((0, oc.M))
    ax.set_ylim((0, y_maxes[title]))
    ax.set_yticks((0, y_maxes[title]))

    # Only label the first axes
    ax.set_xlabel('number of connections', color='C3', labelpad=-10)
    ax.set_ylabel('number of array references', color='C3', labelpad=-25)
    ax.set_xticks((0, oc.M))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return ax


class OpsCounter():
    """Class to count the number of operations in a union-find data type.

    Parameters
    ----------
    UF : UnionFind class
        The class of union-find that will be used to store the connections.
    **kwargs : dict-like
        Any additional parameters will be passed to `UF`.

    Attributes
    ----------
    uf : union-find
        The union-find data type where connections are computed.
    N : int
        Number of sites.
    M : int
        Number of connections attempted.
    ops : list
        List of number of operations performed.
    cost : list
        A cumulative list of the number of array accesses per `connected`,
        `union`, and `find` operation in `uf`.
    tots : list
        A list of the cumulative average number of array accesses per operation
        in `uf`.
    """
    def __init__(self, UF, N, **kwargs):
        self.uf = UF(N, **kwargs)
        self.N = N
        self.M = 0
        self.ops = [0]
        self.cost = list()
        self.totals = list()

    @property
    def tots(self):
        return self.totals / self.ops

    @classmethod
    def fromfile(cls, file, UF, **kwargs):
        N, items = read_uf_file(file)
        return cls.fromitems(items, UF, N, **kwargs)

    @classmethod
    def fromitems(cls, items, UF, N, **kwargs):
        oc = cls(UF, N, **kwargs)
        oc.M = len(items)             # total number of connections
        oc.ops = 1 + np.arange(oc.M)  # number of operations
        for p, q in items:
            if oc.uf.connected(p, q):
                oc.cost.append(oc.uf._cost)
                oc.totals.append(oc.uf._total)
                continue
            oc.uf.union(p, q)
            oc.cost.append(oc.uf._cost)
            oc.totals.append(oc.uf._total)
        return oc


# ----------------------------------------------------------------------------- 
#         Compute the operation costs from the given input file
# -----------------------------------------------------------------------------
file = Path('./data/mediumUF.txt')

fig = plt.figure(1, clear=True, constrained_layout=True)
fig.set_size_inches((8, 10), forward=True)

# Define plot locations by their names!
axd = fig.subplot_mosaic(
    [
        ['quick-find', 'weighted quick-find'],
        ['quick-union', 'quick-union (path compression)'],
        ['weighted quick-union', 'weighted quick-union (path compression)'],
    ],
    empty_sentinel='X',
    gridspec_kw=dict(height_ratios=[10, 2, 1], hspace=0.05)
)

ufs = [QuickFindUF,
       QuickUnionUF,
       WeightedQuickUnionUF,
       WeightedQuickFindUF,
       QuickUnionUF,          # slightly awkward to have to add 2x
       WeightedQuickUnionUF]

# Match book figure
y_maxes = dict({'quick-find': 1300,
                'quick-union': 110,
                'weighted quick-union': 20,
                'weighted quick-find': 1300,
                'quick-union (path compression)': 110,
                'weighted quick-union (path compression)': 20,
                })

titles = y_maxes.keys()

for i, (UF, title) in enumerate(zip(ufs, titles)):
    # Manually iterate through connections to track costs along the way
    if 'path compression' in title:
        oc = OpsCounter.fromfile(file, UF, compress_paths=True)
    else:
        oc = OpsCounter.fromfile(file, UF)

    # Plot the data
    ax = fig.add_subplot(axd[title])
    cost_plot(oc, ax=ax, y_max=y_maxes[title])

    # Turn off labels for all but first axes
    if i > 0:
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticks([])

plt.show()
# =============================================================================
# =============================================================================
