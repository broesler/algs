#!/usr/bin/env python3
# =============================================================================
#     File: perfect_maze.py
#  Created: 2022-07-18 19:59
#   Author: Bernie Roesler
#
"""
Undirected Graphs, Web Exercise 5. Generate a perfect maze.
"""
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt

from random import shuffle

from algs.graph import EuclideanGraph, spanning_tree_dfs, DepthFirstPaths
from algs.graph.random import full_grid_graph

V = 25
START = 0
END = V**2 // 2  # center of maze

# The maze is a spanning tree of the graph!
G = full_grid_graph(V, random=True)
T = EuclideanGraph(G=spanning_tree_dfs(G, 0), x=G.x, y=G.y)

# Solve the maze
dfs = DepthFirstPaths(T, START)
assert dfs.has_path_to(END)
P = dfs.path_to(END)

# Plot the spanning tree, i.e. the path through the maze
fig, ax = plt.subplots(num=1, clear=True, constrained_layout=True)
# G.draw(ax=ax, c='k', vkws=dict(s=1), ekws=dict(alpha=0.1))

# TODO actually plot walls of maze between unconnected vertices
# Use large linewidth to simulate "walls" of maze
T.draw(ax=ax, ekws=dict(lw=15))

# Plot the start, end, and solution!
ax.scatter(G.x[START], G.y[START], c='C2', s=50, zorder=10)
ax.scatter(G.x[END], G.y[END], c='C3', s=50, zorder=10)
T.draw(ax=ax, p=P, c='C0', ekws=dict(lw=3))

plt.show()

# =============================================================================
# =============================================================================
