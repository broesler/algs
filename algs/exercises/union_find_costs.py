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

file = Path('./data/mediumUF.txt')
N, items = read_uf_file(file)
M = len(items)      # total number of connections
ops = 1 + np.arange(M)  # number of operations

fig = plt.figure(1, clear=True, constrained_layout=True)
fig.set_size_inches((8, 10), forward=True)

mosaic = [
        ['quick-find', 'weighted quick-find'],
        ['quick-union', 'X'],
        ['weighted quick-union', 'X'],
    ]
axd = fig.subplot_mosaic(
        mosaic,
        empty_sentinel='X',
        gridspec_kw=dict(height_ratios=[10, 2, 1], hspace=0.05)
    )

ufs = [QuickFindUF, QuickUnionUF, WeightedQuickUnionUF, WeightedQuickFindUF]
titles = ['quick-find', 'quick-union',
          'weighted quick-union', 'weighted quick-find']

# Match book figure
y_maxes = dict({'quick-find': 1300, 'weighted quick-find': 1300,
                'quick-union': 110, 'weighted quick-union': 20,})

for i, (UF, title) in enumerate(zip(ufs, titles)):
    # Manually iterate through connections to track costs along the way
    uf = UF(N)
    costs = list()
    totals = list()
    for p, q in items:
        if uf.connected(p, q):
            costs.append(uf._cost)
            totals.append(uf._total)
            continue
        uf.union(p, q)
        costs.append(uf._cost)
        totals.append(uf._total)

    tots = totals / ops

    # Plot the data
    ax = fig.add_subplot(axd[title])
    ax.scatter(ops, costs, color=0.7*np.r_[1, 1, 1], s=1, alpha=0.8)
    ax.scatter(ops, tots, c='C3', s=1, alpha=0.8)

    # Label the final average total cost value
    ax.annotate(rf"{tots[-1]:.0f}",
                xy=(M, tots[-1]), xycoords='data',
                xytext=(1.1*M, 1.1*tots[-1]), textcoords='data',
                ha='center', va='bottom', color='C3',
                arrowprops=dict(arrowstyle="-|>", color="C3"))

    ax.set_title(title, color='C3', fontweight='bold', fontsize=9, 
                 x=-0.1, ha='left', pad=10, va='bottom')

    ax.set_xlim((0, M))
    ax.set_ylim((0, y_maxes[title]))
    ax.set_yticks((0, y_maxes[title]))

    # Only label the first axes
    if i == 0:
        ax.set_xlabel('number of connections', color='C3', labelpad=-10)
        ax.set_ylabel('number of array references', color='C3', labelpad=-25)
        ax.set_xticks((0, M))
    else:
        ax.set_xticks([])

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.show()
# =============================================================================
# =============================================================================
