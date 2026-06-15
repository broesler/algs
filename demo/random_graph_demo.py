#!/usr/bin/env python3
# =============================================================================
#     File: random_graph_demo.py
#  Created: 2026-06-15 14:12
#   Author: Bernie Roesler
# =============================================================================

"""Demonstrate random graph generation."""

import matplotlib.pyplot as plt

from algs.graph.random import (
    erdos_renyi,
    random_euclidean_graph,
    random_grid_graph,
    random_interval_graph,
    random_simple_graph,
)

# Define the parameters
V, E = 10, 9

# Random graphs
G = erdos_renyi(V, E)
print(G)

Gs = random_simple_graph(V, E)
print(Gs)

# TODO plot these intervals?
sgi = random_interval_graph(V=5, d=0.1)

# -----------------------------------------------------------------------------
#         Euclidean Graphs
# -----------------------------------------------------------------------------
Ge = random_euclidean_graph(V, d=0.5)
Gb = random_euclidean_graph(V, connected=True)

fig, ax = plt.subplots(num=1, clear=True, constrained_layout=True)
Ge.draw(ax=ax, label_nodes=True)
Gb.draw(ax=ax, label_nodes=True, c='tab:blue')
plt.show()

# -----------------------------------------------------------------------------
#         Grid Graph
# -----------------------------------------------------------------------------
Gg = random_grid_graph(V, R=20, dist_edges=True)

fig, ax = plt.subplots(num=2, clear=True, constrained_layout=True)
Gg.draw(ax=ax)


plt.show()

# =============================================================================
# =============================================================================
