#!/usr/bin/env python3
# =============================================================================
#     File: point2d.py
#  Created: 2022-06-09 23:21
#   Author: Bernie Roesler
#
"""
1.2.1 Point2D client to generate N random points and compute the distance
between the *closest* pair.

See Also
--------
`Wikipedia <https://en.wikipedia.org/wiki/Closest_pair_of_points_problemite_ref-7>`_
`Rabin Flips a Coin <https://rjlipton.wpcomstaging.com/2009/03/01/rabin-flips-a-coin/>`_
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


def closest_pair_naive(points):
    """Naïve O(N²) algorithm.

    Parameters
    ----------
    points : list of :obj:`Point2D`

    Returns
    -------
    a, b : tuple of int
        The list indices corresponding to the two closest points.
    """
    N = len(points)
    D = np.full((N, N), np.nan)
    for i in range(N):
        for j in range(i):
            D[i, j] = points[i].dist_to(points[j])

    i_min, j_min = np.unravel_index(np.nanargmin(D), D.shape)
    return points[i_min], points[j_min]


def bounding_box(points):
    """Return the corners of the bouding box of the list of points."""
    xs = sorted(points, key=Point2D.X_ORDER)
    ys = sorted(points, key=Point2D.Y_ORDER)
    return Point2D(xs[0].x, ys[0].y), Point2D(xs[-1].x, ys[-1].y)


# def closest_pair_rabin(points):
#     """Implement the Rabin (1976) algorithm.

#     Parameters
#     ----------
#     points : list of :obj:`Point2D`

#     Returns
#     -------
#     a, b : tuple of int
#         The list indices corresponding to the two closest points.
#     """
#     N = len(points)
# Sample n pairs of points
n = int(N**0.5)
idx = rng.choice(N, size=(n, 2), replace=False)
# Select grid size from minimum distance between pairs
d = min([points[a].dist_to(points[b]) for a, b in idx])
assert d > 0
# Create d-by-d grid on bounding box of points
p0, p1 = bounding_box(points)
y, x = np.mgrid[p0.x-d:p1.x+d:d, p0.y-d:p1.y+d:d]
# return y, x


an, bn = closest_pair_naive(points)

# ----------------------------------------------------------------------------- 
#         Plot
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()

# Plot the Rabin grid
# ax.scatter(x, y, c='C2', s=20, alpha=0.5)
ax.plot(x, y, c='C2', alpha=0.5)
ax.plot(x.T, y.T, c='C2', alpha=0.5)

for p in points:
    p.draw(color=0.7*np.ones(3))

# Plot the random pairs of points
markers = ['o', 's', 'x', 'v', '^', 'd', '*', '<', '>']
for k, (i, j) in enumerate(idx):
    marker = markers[k % len(markers)]
    points[i].draw(marker=marker, c='k', s=50)
    points[j].draw(marker=marker, c='k', s=50)


# Highlight the closest pait
an.draw(c='C3')
bn.draw(c='C3')
an.draw_to(bn, c='C3')

ax.set(xlabel='x', #xlim=(-0.02, 1.02),
       ylabel='y', #ylim=(-0.02, 1.02),
       aspect='equal',)
ax.grid(False)

plt.show()

# =============================================================================
# =============================================================================
