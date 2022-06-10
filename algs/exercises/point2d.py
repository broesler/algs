#!/usr/bin/env python3
# =============================================================================
#     File: point2d.py
#  Created: 2022-06-09 23:21
#   Author: Bernie Roesler
#
"""
1.2.1 Point2D client to generate N random points and compute the distance
between the *closest* pair.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np

from algs.adt import Point2D

rng = np.random.default_rng(seed=565656)
N = 50

# Generate N random points in the unit square
points = []
for i in range(N):
    points.append(Point2D(*rng.random(2)))

# Naïve O(N²) algorithm
D = np.full((N, N), np.nan)
for i in range(N):
    for j in range(i):
        D[i, j] = points[i].dist_to(points[j])

i_min, j_min = np.unravel_index(np.nanargmin(D), D.shape)
a, b = points[i_min], points[j_min]

# ----------------------------------------------------------------------------- 
#         Plot
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()

for p in points:
    p.draw(color=0.7*np.ones(3))

# Highlight the closest pait
a.draw(c='C3')
b.draw(c='C3')
a.draw_to(b, c='C3')

ax.set(xlabel='x', xlim=(-0.02, 1.02),
       ylabel='y', ylim=(-0.02, 1.02),
       aspect='equal',)
ax.grid(False)

plt.show()

# =============================================================================
# =============================================================================
