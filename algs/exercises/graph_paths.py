#!/usr/bin/env python3
# =============================================================================
#     File: graph_paths.py
#  Created: 2022-06-22 16:46
#   Author: Bernie Roesler
#
"""
Draw the graphs on p 542.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np

from algs.graph import (Graph, EuclideanGraph, CC, DepthFirstPaths,
                        BreadthFirstPaths)

rng = np.random.default_rng(seed=565656)

G = Graph.fromfile('../data/mediumG.txt')
x, y = rng.random((2, G.V))
G = EuclideanGraph(G, x, sorted(y))

assert CC(G).is_connected

# ----------------------------------------------------------------------------- 
#         Search through the graph for the longest path
# -----------------------------------------------------------------------------
# Make DFS spanning tree
# dfs = DepthFirstPaths(G, 0)
# dedges = set()
# for v in G.vertices():
#     path = dfs.path_to(v)
#     for i in range(len(path)-1):
#         edge = (path[i], path[i+1])
#         if (edge[1], edge[0]) not in dedges:
#             dedges.add(edge)

ms = 0  # source
mv = 0  # end vertex
md = 0  # path length
dpath = None
for s in G.vertices():
    dfs = DepthFirstPaths(G, s)
    assert all(dfs._marked)  # indeed a spanning tree
    for v in G.vertices():
        path = dfs.path_to(v)
        if len(path) > md:
            ms = s
            mv = v
            md = len(path)
            dpath = list(path)

# Make BFS spanning tree
bfs = BreadthFirstPaths(G, s)
# Define paths by dist_to rankings?

# ----------------------------------------------------------------------------- 
#         Plot the graph
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True, constrained_layout=True)
dp = 0.2
ps = np.arange(dp, 1+dp, dp)
gs = fig.add_gridspec(nrows=len(ps), ncols=2)
# Plot 20, 40, 60, 80, 100% of path length
for i, p in enumerate(ps):
    # Plot DFS
    ax = fig.add_subplot(gs[i, 0])
    G.draw(ax=ax, c='#EEE', vkws=dict(s=20, alpha=0.8), ekws=dict(alpha=0.8))
    N = int(p*len(dpath))
    G.draw(ax=ax, p=dpath[:N], vkws=dict(s=20, alpha=0.8), ekws=dict(alpha=0.8))
    ax.set_title(f"{100*p:.0f}%", color='C3', fontsize=9,
                 x=0, ha='left', pad=0, va='bottom')

    # Plot BFS
    # ax = fig.add_subplot(gs[i, 0])
    # G.draw(ax=ax, c='#EEE', vkws=dict(s=20, alpha=0.8), ekws=dict(alpha=0.8))
    # N = int(p*len(dpath))
    # G.draw(ax=ax, p=dpath[:N], vkws=dict(s=20, alpha=0.8), ekws=dict(alpha=0.8))
    # ax.set_title(f"{100*p:.0f}%", color='C3', fontsize=9,
    #              x=0, ha='left', pad=0, va='bottom')

plt.show()

# =============================================================================
# =============================================================================
