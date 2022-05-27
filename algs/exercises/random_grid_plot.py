#!/usr/bin/env python3
# =============================================================================
#     File: random_grid_plot.py
#  Created: 2022-05-27 10:19
#   Author: Bernie Roesler
#
"""
Exercise 1.5.18-19. Generate a random grid and connect with UnionFind.
"""
# =============================================================================

import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import numpy as np
import pandas as pd

from algs.unionfind import random_grid, WeightedQuickUnionUF

N = 5
g = random_grid(N)

y, x = np.mgrid[:N, :N]
x, y = np.ravel(x), np.ravel(y)

fig = plt.figure(1, clear=True, tight_layout=True)
ax = fig.add_subplot()
ax.scatter(x, y, c='k', zorder=2)
for p, q in g:
    ax.plot((x[p], x[q]), (y[p], y[q]), 'k-', lw=2)

# Label the nodes
trans_offset = mtransforms.offset_copy(ax.transData, fig=fig,
                                        x=-5, y=5, units='points')
for i, (xn, yn) in enumerate(zip(x, y)):
    ax.text(xn, yn, f"{i}", ha='right', va='bottom', transform=trans_offset)

ax.set_aspect('equal')
ax.invert_yaxis()  # top-down as drawn by hand
# ax.grid('on')
ax.axis('off')  # hide everything but the grid

plt.show()
# =============================================================================
# =============================================================================
