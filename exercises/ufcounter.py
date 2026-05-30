#!/usr/bin/env python3
# =============================================================================
#     File: ufcounter.py
#  Created: 2022-05-26 15:56
#   Author: Bernie Roesler
# =============================================================================

"""Define the Union-Find Counter class."""

import numpy as np
from tqdm import tqdm

from algs.unionfind import read_uf_file


def cost_plot(oc, ax=None, title='', y_max=0):
    """Plot amortized costs.

    Parameters
    ----------
    oc : :obj:ufcounter
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
    ax.scatter(oc.ops, oc.cost, color=0.7 * np.r_[1, 1, 1], s=1, alpha=0.8)
    ax.scatter(oc.ops, oc.tots, c='C3', s=1, alpha=0.8)

    # Label the final average total cost value
    ax.annotate(
        rf"{oc.tots[-1]:.0f}",
        xy=(oc.M, oc.tots[-1]),
        xycoords='data',
        xytext=(1.1 * oc.M, 1.1 * oc.tots[-1]),
        textcoords='data',
        ha='center',
        va='bottom',
        color='C3',
        arrowprops={'arrowstyle': "-|>", 'color': "C3"},
    )

    ax.set_title(
        title,
        color='C3',
        fontweight='bold',
        fontsize=9,
        x=0,
        ha='left',
        pad=10,
        va='bottom',
    )

    ax.set_xlim((0, oc.M))

    if y_max:
        ax.set_ylim((0, y_max))
        ax.set_yticks((0, y_max))

    # Only label the first axes
    ax.set_xlabel('number of connections', color='C3', labelpad=-10)
    ax.set_ylabel('number of array references', color='C3', labelpad=-10)
    ax.set_xticks((0, oc.M))

    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return ax


class UFCounter:
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
        self.cost = []
        self.totals = []

    @property
    def tots(self):
        """Cumulative average total cost per operation."""
        return self.totals / self.ops

    @classmethod
    def fromfile(cls, file, UF, **kwargs):
        """Create a UFCounter from a file containing connections."""
        N, items = read_uf_file(file)
        return cls.fromitems(items, UF, N, **kwargs)

    @classmethod
    def fromitems(cls, items, UF, N, verbose=False, **kwargs):
        """Create a UFCounter from an iterable of connections."""
        oc = cls(UF, N, **kwargs)
        oc.M = len(items)  # total number of connections
        oc.ops = 1 + np.arange(oc.M)  # number of operations
        iters = tqdm(items) if verbose else items
        for p, q in iters:
            if oc.uf.connected(p, q):
                oc.cost.append(oc.uf._cost)
                oc.totals.append(oc.uf._total)
                continue
            oc.uf.union(p, q)
            oc.cost.append(oc.uf._cost)
            oc.totals.append(oc.uf._total)
        return oc


# =============================================================================
# =============================================================================
