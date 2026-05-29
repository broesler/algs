#!/usr/bin/env python3
# =============================================================================
#     File: graph_density_plot.py
#  Created: 2022-07-21 16:10
#   Author: Bernie Roesler
# =============================================================================

"""Draw the graphs on p 520 (sparse vs. dense)."""

import matplotlib.pyplot as plt
import numpy as np

from algs.graph import EuclideanGraph, random_simple_graph

V = 50
Es = [200, 1000]
tags = ['sparse', 'dense']

rng = np.random.default_rng(seed=19900416)
x, y = rng.random((2, V))

fig = plt.figure(1, clear=True, constrained_layout=True)
fig.set_size_inches((8, 4), forward=True)
fig.suptitle(rf"Two graphs, ($V$ = {V})")
gs = fig.add_gridspec(ncols=2)

for g, E, tag in zip(gs, Es, tags):
    G = EuclideanGraph(random_simple_graph(V, E), x, y)
    ax = fig.add_subplot(g)
    G.draw()
    ax.set_title(
        rf"{tag} ($E$ = {E})",
        color='C3',
        fontsize=9,
        x=0,
        ha='left',
        pad=10,
        va='bottom',
    )

plt.show()

# =============================================================================
# =============================================================================
