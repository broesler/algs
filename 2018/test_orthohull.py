#!/Users/bernardroesler/anaconda3/envs/insight/bin/python3
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
filename = './data/wiki_orthohull.dat'
# filename = './data/test_input06_b.dat'
coords = np.loadtxt(filename, delimiter=', ') #, max_rows=6)

# Scale up to all integers
coords = 10.0*(coords.round(1).astype(int))

# Convenience arrays
x, y = coords[:, 0], coords[:, 1]

# Ignore convex hull points (guaranteed to have infinite areas
hull = geom.ConvexHull(coords, kind='orthogonal')

# TODO other idea: find all points that are "closest" to each point on the
# bounding box? Any point that is closest to a point on the bounding box will
# have a Voronoi cell that "escapes", i.e. has infinite area.

#------------------------------------------------------------------------------
#        Plots
#------------------------------------------------------------------------------
fig = plt.figure(1, clear=True)
ax = fig.add_subplot(111)

# Data points
ax.scatter(x, y, s=30, c='k', marker='x')

# Convex Hull
ax.scatter(coords[hull.vertices, 0], coords[hull.vertices, 1], 
           marker='x', c='r', s=30)

ax.set_xlabel(r'$x$')
ax.set_ylabel(r'$y$')
ax.grid(zorder=0)
ax.set_aspect('equal')

plt.show()
#==============================================================================
#==============================================================================
