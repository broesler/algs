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
N = 100  # FIXME Rabin algorithm fails for N = 20 with seed=565656

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


def round_to_grid(p, d=1.0):
    """Round the point `p` to the nearest grid point."""
    xg = d * np.floor(p.x / d + 0.5)
    yg = d * np.floor(p.y / d + 0.5)
    return Point2D(xg, yg)


def closest_pair_rabin(points, plot=False, ax=None):
    """Implement the Rabin (1976) algorithm.

    Parameters
    ----------
    points : list of :obj:`Point2D`

    Returns
    -------
    a, b : tuple of int
        The list indices corresponding to the two closest points.
    """
    if plot and ax is None:
        ax = plt.gca()

    # Sample √N pairs of points without replacement
    N = len(points)
    n = int(N**0.5)
    idx = rng.choice(N, size=(n, 2), replace=False)

    # Select grid size from minimum distance between pairs
    d = min([points[a].dist_to(points[b]) for a, b in idx])
    assert d > 0

    # Create d-by-d grid on bounding box of points
    p0, p1 = bounding_box(points)
    # grid includes origin, but only need points in vicinity of `points`
    p0, p1 = round_to_grid(p0), round_to_grid(p1)

    # Round the points to their nearest grid point, storing in a hash table
    grid = dict()
    for p in points:
        g = round_to_grid(p, d)
        if g not in grid:
            grid[g] = list()
        grid[g].append(p)

    # For each input point, compute the distance to all other points at the
    # same grid point, or any grid point within the neighborhood
    i_min = None
    j_min = None
    q_min = None
    d_min = float('inf')
    for i, p in enumerate(points):
        g = round_to_grid(p, d)
        keys = [g,                      # center
                Point2D(g.x-d, g.y),    # left
                Point2D(g.x+d, g.y),    # right
                Point2D(g.x, g.y-d),    # down
                Point2D(g.x, g.y+d),    # up
                Point2D(g.x-d, g.y-d),  # bottom left
                Point2D(g.x-d, g.y+d),  # top left
                Point2D(g.x+d, g.y-d),  # bottom right
                Point2D(g.x+d, g.y+d),  # top right
                ]
        for k in keys:
            try:
                qs = grid[k]
            except KeyError:
                continue
            for q in qs:
                if p == q:
                    continue
                test = p.dist_to(q)
                if test < d_min:
                    i_min = i
                    q_min = q
                    d_min = test

    j_min = points.index(q_min)  # linear search, could use IndexSet.

    if plot:
        # # Plot all of the points
        # for p in points:
        #     p.draw(color=0.7*np.ones(3))

        # Plot the random pairs of points
        # markers = ['o', 's', 'x', 'v', '^', 'd', '*', '<', '>']
        # for k, (i, j) in enumerate(idx):
        #     marker = markers[k % len(markers)]
        #     points[i].draw(marker=marker, c='k', s=50)
        #     points[j].draw(marker=marker, c='k', s=50)

        # Plot the grid
        yg, xg = np.mgrid[p0.x:p1.x+d:d, p0.y:p1.y+d:d]
        # ax.scatter(xg, yg, c='C2', s=20, alpha=0.5)
        ax.plot(xg, yg, c='C2', alpha=0.5)
        ax.plot(xg.T, yg.T, c='C2', alpha=0.5)

        # Plot the closest grid points
        for g, ps in grid.items():
            for p in ps:
                ax.plot((p.x, g.x), (p.y, g.y), '-k', zorder=0)

    return points[i_min], points[j_min]


# -----------------------------------------------------------------------------
#         Plot
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()

an, bn = closest_pair_naive(points)
a, b = closest_pair_rabin(points, plot=True)
# assert np.isclose(an.dist_to(bn), a.dist_to(b))

for p in points:
    p.draw(color=0.7*np.ones(3), s=20)

# Highlight the closest pair(s)
an.draw(c='C2')
bn.draw(c='C2')
an.draw_to(bn, c='C2')
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
