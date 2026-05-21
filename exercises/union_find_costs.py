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
from pathlib import Path

from ufcounter import cost_plot, UFCounter

from algs.unionfind import (QuickFindUF, QuickUnionUF,
                            WeightedQuickUnionUF, WeightedQuickFindUF)

# -----------------------------------------------------------------------------
#         Compute the operation costs from the given input file
# -----------------------------------------------------------------------------
file = Path('../data/mediumUF.txt')

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
        oc = UFCounter.fromfile(file, UF, compress_paths=True)
    else:
        oc = UFCounter.fromfile(file, UF)

    # Plot the data
    ax = fig.add_subplot(axd[title])
    cost_plot(oc, ax=ax, title=title, y_max=y_maxes[title])

    # Turn off labels for all but first axes
    if i > 0:
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticks([])

plt.show()
# =============================================================================
# =============================================================================
