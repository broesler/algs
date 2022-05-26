#!/usr/bin/env python3
# =============================================================================
#     File: union_find_largecosts.py
#  Created: 2022-05-26 16:00
#   Author: Bernie Roesler
#
"""
Amortized cost plots of the union-find datatypes.
"""
# =============================================================================

import matplotlib.pyplot as plt
from pathlib import Path

from opscounter import cost_plot, OpsCounter

from algs.unionfind import QuickUnionUF, WeightedQuickUnionUF

# -----------------------------------------------------------------------------
#         Compute the operation costs from the given input file
# -----------------------------------------------------------------------------
file = Path('../data/largeUF.txt')

fig = plt.figure(1, clear=True, constrained_layout=True)
fig.set_size_inches((8, 10), forward=True)

# Define plot locations by their names!
axd = fig.subplot_mosaic(
    [
        ['quick-union (path compression)'],
        ['weighted quick-union'],
    ],
    gridspec_kw=dict(height_ratios=[2, 1], hspace=0.05)
)

# Match book figure
ufs = [QuickUnionUF, WeightedQuickUnionUF]
y_maxes = dict({'quick-union (path compression)': 60,
                'weighted quick-union': 20})
# ufs = [WeightedQuickUnionUF]
# y_maxes = dict({'weighted quick-union': 20})
titles = y_maxes.keys()

for i, (UF, title) in enumerate(zip(ufs, titles)):
    if 'path compression' in title:
        oc = OpsCounter.fromfile(file, UF, compress_paths=True, verbose=True)
    else:
        oc = OpsCounter.fromfile(file, UF, verbose=True)

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
