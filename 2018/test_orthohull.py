#!/usr/bin/env python3
#==============================================================================
#     File: test_orthohull.py
#  Created: 2019-02-13 22:06
#   Author: Bernie Roesler
#
"""
  Description:
"""
#==============================================================================

import re
import numpy as np
import matplotlib.pyplot as plt
from scipy import spatial

import geometry as geom

# Load the file (the easy way!)
filename = './test_data/wiki_orthohull_int2.dat'
# filename = './test_data/test_input06.dat'
# filename = './test_data/test_input06_b.dat'  # degenerate case, no interior points!
# filename = './data/input06.dat'
points = np.loadtxt(filename, delimiter=', ') #, max_rows=6)

# './test_data/wiki_orthohull_int2.dat' contains "escaping" points, and interior
# corner points on the orthogonal hull that have finite Voronoi cells

# Convenience arrays
x, y = points[:, 0], points[:, 1]

# Ignore convex hull points (guaranteed to have infinite areas
# hull = geom.ConvexHull(points, kind='orthogonal')
hull = geom.BoundingSet(points)
bb = hull._bounding_box()

#------------------------------------------------------------------------------
#        Plots
#------------------------------------------------------------------------------
fig = plt.figure(1, clear=True)
ax = fig.add_subplot(111)

# Bounding box
ax.scatter(bb[:, 0], bb[:, 1], 
           s=30, marker='o', edgecolors='b', facecolors='none')

# Data points
ax.scatter(x, y, s=30, c='k', marker='x')

# Convex Hull
ax.scatter(points[hull.vertices, 0], points[hull.vertices, 1], 
           marker='x', c='r', s=30)

ax.set_xlabel(r'$x$')
ax.set_ylabel(r'$y$')
ax.grid(zorder=0)
ax.set_aspect('equal')

plt.show()
#==============================================================================
#==============================================================================
