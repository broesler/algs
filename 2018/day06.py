#!/Users/bernardroesler/anaconda3/envs/insight/bin/python3
#==============================================================================
#     File: day06.py
#  Created: 2019-01-28 22:39
#   Author: Bernie Roesler
#
"""
  Description: Manhattan Areas
"""
#==============================================================================

import re
import numpy as np
import matplotlib.pyplot as plt
from scipy import spatial

import geometry as geom

# Load the file (the easy way!)
filename = './data/wiki_orthohull.dat'
# filename = './data/test_input06.dat'
# filename = './data/test_input06_b.dat'
# filename = './data/input06.dat'
coords = np.loadtxt(filename, delimiter=', ') #, max_rows=6)

# Convenience arrays
x, y, angles = np.array([(p[0], p[1], geom.theta_deg(p[1], p[0])) for p in coords]).T

# Algorithm:
#   * compute Voronoi vertices (using Manhattan distance!!)
#   * compute area of finite Voronoi cells
#   * return maximum of areas (count integral points in polygon)

# Brute-force:
#   * generate grid of max/min coords
#   * run k-NN to classify each grid point
#   * count points in each class
#   * repeat with larger grid until convergence

# Ignore convex hull points (guaranteed to have infinite areas
# hull = spatial.ConvexHull(coords)
hull = geom.ConvexHull(coords, kind='orthogonal')
n_classes = coords.shape[0]
mask = np.ones(n_classes, dtype=bool)
mask[hull.vertices] = False

# Use KDTree to efficiently calculate k-NN of grid points -> coords
kdtree = spatial.cKDTree(coords)

grid_mult = 1.2

xmin, xmax = np.min(x)-1, np.max(x)+1
ymin, ymax = np.min(y)-1, np.max(y)+1
cx = (xmax - xmin) / 2 + xmin    # center coordinate
cy = (ymax - ymin) / 2 + ymin
w = grid_mult * (xmax - xmin)    # width/height
h = grid_mult * (ymax - ymin)
xmin, xmax = int(cx - w/2), int(cx + w/2)  # corners
ymin, ymax = int(cy - h/2), int(cy + h/2)

xg, yg = np.mgrid[xmin:xmax, ymin:ymax]
grid = np.vstack([xg.ravel(), yg.ravel()]).T

dists, classes = kdtree.query(grid, k=1, p=1)  # 1 neighbor, Minkowski p = 1
counts = np.bincount(classes, minlength=n_classes)
areas = np.vstack([np.arange(n_classes), counts]).T
masked = areas[mask]
out = masked[np.argmax(masked[:, 1])]  # tuple based on max area

print(f"Point ID: {out[0]}, Area: {out[1]}")

#------------------------------------------------------------------------------
#        Plots
#------------------------------------------------------------------------------
fig = plt.figure(1, clear=True)
ax = fig.add_subplot(111)

# Categorized grid points
sc = ax.scatter(grid[:, 0], grid[:, 1], s=20,
                c=classes, cmap=plt.cm.get_cmap('viridis', n_classes),
                vmin=-0.5, vmax=n_classes-0.5)  # center labels
cb = plt.colorbar(sc)

# Data points
ax.scatter(x, y, s=30, c='k', marker='x')
ax.scatter(x[out[0]], y[out[0]], s=50, c='b', marker='o')

# Convex hull
ax.scatter(coords[hull.vertices, 0], coords[hull.vertices, 1],
           s=30, marker='x', c='r')

# sc = ax.scatter(x, y, c=angles, vmin=0, vmax=90)
# cb = plt.colorbar(sc)
# cb.ax.set_ylabel(r'$\theta$ [deg]')

# ax.scatter(x[:2], y[:2], marker='x', c='r', s=100)  # highlight points

ax.set_xlabel(r'$x$')
ax.set_ylabel(r'$y$')
ax.grid(zorder=0)
ax.set_aspect('equal')

plt.show()

#==============================================================================
#==============================================================================
