#!/Users/bernardroesler/anaconda3/envs/insight/bin/python3
#==============================================================================
#     File: day06.py
#  Created: 2019-01-28 22:39
#   Author: Bernie Roesler
#
"""
  Description: Manhattan Areas

  Algorithm:
    * compute Voronoi vertices (using Manhattan distance!!)
    * compute area of finite Voronoi cells
    * return maximum of areas (count integral points in polygon)
  
  Current algorithm:
    * generate grid of max/min coords
    * run k-NN to classify each grid point
    x compute orthogonal convex hull vertices
        * NOTE caveat: orthogonal convex hull does NOT guarantee Vorononi cells
        will be finite! 
        * NOTE caveat: orthogonal convex hull does NOT guarantee Vorononi cells
        will be infinite either!! See wiki_orthohull.dat, point (8, 18)
    * Find set of points that are closest to bounding box (via
      Manhattan distance)
    * count points in each class
    * return maximum of counts (excluding BoundingSet)

"""
#==============================================================================

import re
import numpy as np
import matplotlib.pyplot as plt
from scipy import spatial

import geometry as geom

# Load the file (the easy way!)
# filename = './data/wiki_orthohull_int2.dat'
# filename = './data/test_input06.dat'
# filename = './data/test_input06_b.dat'  # degenerate case, no interior points!
filename = './data/input06.dat'
points = np.loadtxt(filename, delimiter=', ') #, max_rows=6)

# Convenience arrays
x, y = points[:, 0], points[:, 1]

# Generate query grid of integer points, arbitrary size
xg, yg = np.mgrid[np.min(x):np.max(x)+1, 
                  np.min(y):np.max(y)+1]
grid = np.vstack([xg.ravel(), yg.ravel()]).T

# Ignore convex hull points (guaranteed to have infinite areas)
# hull = spatial.ConvexHull(coords)
# hull = geom.ConvexHull(coords, kind='orthogonal')
hull = geom.BoundingSet(points)  # not convex, but infinite areas
n_cl = points.shape[0]
mask = np.ones(n_cl, dtype=bool)
mask[hull.vertices] = False

# Use KDTree to efficiently calculate k-NN of grid points -> coords
kdtree = spatial.cKDTree(points)
dists, classes = kdtree.query(grid, k=2, p=1)  # 2 neighbors, Minkowski p = 1

# tag equidistant points with unused class number, so we don't include them
cl = list()
for i, d in enumerate(dists):
    cl.append(classes[i, 0] if d[0] != d[1] else n_cl)
cl = np.asarray(cl)

# Sum up areas of each Voronoi cell
counts = np.bincount(cl, minlength=n_cl+1)  # extra bin for equidistant pts
areas = np.vstack([np.arange(n_cl), counts[:-1]]).T  # skip "unused" class

#------------------------------------------------------------------------------ 
#        Part 1
#------------------------------------------------------------------------------
if np.any(mask):
    masked = areas[mask]
    out = masked[np.argmax(masked[:, 1])]  # tuple based on max area
    print(f"Point ID: {out[0]}, Area: {out[1]}")  # Point ID: 41, Area: 3989
else:
    import warnings
    warnings.warn('Degenerate case! All cells have infinite area!')
    out = [slice(0,0)]  # ignore plot command below

#------------------------------------------------------------------------------ 
#        Part 2
#------------------------------------------------------------------------------
# What is the size of the region containing all locations which have a total
# distance to all given coordinates of less than 10000?
thresh = 10000
grid_add = thresh / points.shape[0]
xg, yg = np.mgrid[np.min(x)-grid_add-1:np.max(x)+grid_add+1, 
                  np.min(y)-grid_add-1:np.max(y)+grid_add+1]
grid2 = np.vstack([xg.ravel(), yg.ravel()]).T
grid_dists = spatial.distance_matrix(grid2, points, p=1)
gd_sum = grid_dists.sum(axis=1)

out2 = np.sum(gd_sum < thresh)
print(f'Area: {out2}')

#------------------------------------------------------------------------------
#        Plots
#------------------------------------------------------------------------------
fig = plt.figure(1, clear=True)
ax = fig.add_subplot(111)

# Categorized grid points
sc = ax.scatter(grid[:, 0], grid[:, 1], s=20,
                c=cl, cmap=plt.cm.get_cmap('viridis', n_cl+1),
                vmin=-0.5, vmax=n_cl+1-0.5)  # center labels
cb = plt.colorbar(sc)

# Data points
ax.scatter(x, y, s=30, c='k', marker='x')
ax.scatter(x[out[0]], y[out[0]], s=80,
           marker='o', edgecolors='r', facecolors='none')

# Convex hull
ax.scatter(points[hull.vertices, 0], points[hull.vertices, 1],
           s=30, marker='x', c='r')

ax.set_xlabel(r'$x$')
ax.set_ylabel(r'$y$')
ax.grid(zorder=0)
ax.set_aspect('equal')

plt.show()

#==============================================================================
#==============================================================================
