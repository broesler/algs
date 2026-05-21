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
import numpy as np
import pandas as pd

from algs.unionfind import (full_grid, random_grid, plot_grid, 
                            WeightedQuickUnionUF)

# Generate a random grid
N = 25              # 625 sites
f = full_grid(N)    # grid with all connections
g = random_grid(N)  # grid with random connections but only one group

# Connect components using UnionFind
uf = WeightedQuickUnionUF(N*N, items=g, store=True)
assert uf.count == 1

# Plot the full grid with random connections overlaid
fig, ax = plt.subplots(num=1, clear=True, tight_layout=True)
fig.set_size_inches((8, 8), forward=True)
plot_grid(N, f, label_nodes=False, fig=fig, ax=ax, alpha=0.1)
plot_grid(N, uf.edges, label_nodes=False, fig=fig, ax=ax)
ax.set_title(f"{N = }, {N*N = }")

plt.show()
# =============================================================================
# =============================================================================
