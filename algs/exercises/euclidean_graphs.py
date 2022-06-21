#!/usr/bin/env python3
# =============================================================================
#     File: euclidean_graphs.py
#  Created: 2022-06-20 21:44
#   Author: Bernie Roesler
#
"""
Exercise 4.1.37: Plotting graphs.
"""
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from algs.graph import EuclideanGraph, BreadthFirstPaths, DepthFirstPaths_nr

G = EuclideanGraph.fromfile('../data/tinyG2.txt')
# See p 558
x, y = np.array([[0,  5],
                 [1,  1],
                 [1,  4],
                 [2,  3.5],
                 [2,  1.5],
                 [0,  3],
                 [2,  5],
                 [0,  2],
                 [1,  2],
                 [1,  0],
                 [1,  3],
                 [0,  1]]).T
G.set_coordinates(G.vertices(), x, y)

s = 0
i = 10
dfs = DepthFirstPaths_nr(G, s)
pd = dfs.path_to(i)

bfs = BreadthFirstPaths(G, s)
pb = bfs.path_to(i)

fig, ax = plt.subplots(num=1, clear=True, constrained_layout=True)
G.draw(ax=ax, label_nodes=True)
G.draw(p=pd, ax=ax, label_nodes=True, ekws=dict(lw=3))
G.draw(p=pb, ax=ax, label_nodes=True, 
       vkws=dict(edgecolor='C0'),
       ekws=dict(c='C0'))

dl = Line2D([0, 1], [0, 1], c='C3')
bl = Line2D([0, 1], [0, 1], c='C0')
ax.legend([dl, bl], [f"DFS({s}, {i})", f"BFS({s}, {i})"], 
          loc='upper left', bbox_to_anchor=(1, 1))

plt.show()

# =============================================================================
# =============================================================================
