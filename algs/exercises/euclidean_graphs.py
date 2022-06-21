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

from algs.graph import EuclideanGraph

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

fig, ax = plt.subplots(num=1, clear=True, constrained_layout=True)
G.draw(ax=ax, label_nodes=True)
plt.show()

# =============================================================================
# =============================================================================
