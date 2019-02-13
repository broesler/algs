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

from geometry import Point

pat = re.compile(r'(\d+), (\d+)')

def parse(line):
    """Convert string '123, 45\n' to Point of integers Point(123, 45)."""
    data = line.rstrip()
    res = pat.match(data)
    x, y = int(res.group(1)), int(res.group(2))
    return Point((x, y))

filename = './data/input06.dat'
with open(filename, 'r') as file:
    coords = [parse(x) for x in file.readlines()[:6]]

# Convenience arrays
x, y, angles = np.array([(p.x, p.y, p.theta_deg) for p in coords]).T

# Brute force:
# * compute Voronoi vertices/polygons, labeled by point ID
# * compute areas of polygons
#   x create integer grid that circumscribes max dimensions of Voronoi diagram
#       x brute force: max dims of points, then expand grid until convergence
#   x classify grid points via 1-NN
#   x count points labeled in each class
# * take maximum finite area
#   x take maximum count, excluding convex hull of centroids

xg, yg = np.meshgrid(np.arange(np.min(x), np.max(x)),
                     np.arange(np.min(y), np.max(y)),
                     indexing='ij')

#------------------------------------------------------------------------------ 
#        Plots
#------------------------------------------------------------------------------
fig = plt.figure(1, clear=True)
ax = fig.add_subplot(111)
# ax.scatter(xg, yg, c='k', s=1, alpha=0.2)
sc = ax.scatter(x, y, c=angles, vmin=0, vmax=90)
# ax.scatter(x[:2], y[:2], marker='x', c='r', s=100)  # highlight points

cb = plt.colorbar(sc)
cb.ax.set_ylabel(r'$\theta$ [deg]')
ax.set_xlabel(r'$x$')
ax.set_ylabel(r'$y$')
ax.grid()
ax.set_aspect('equal')
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)

plt.show()
#==============================================================================
#==============================================================================
