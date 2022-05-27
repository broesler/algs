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
N = 5
# g = full_grid(N)
g = random_grid(N)

# Connect components using UnionFind
uf = WeightedQuickUnionUF(N*N, items=g, store=True)

# Plot
fig, ax = plt.subplots(num=1, clear=True, tight_layout=True)
plot_grid(N, uf.made_connections, label_nodes=True, fig=fig, ax=ax)

plt.show()
# =============================================================================
# =============================================================================
