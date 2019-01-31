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
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns

pat = re.compile(r'(\d+), (\d+)')

class Point():
    """Geometric point class."""
    def __init__(self, c=(0, 0)):
        self.c = np.array(c)
        self.dims = len(self.c)
        # Shorthand for 2D points
        self.x = self.c[0]
        if len(self.c) > 1:
            self.y = self.c[1]

    # TODO make setters for these, as well as (x, y)
    @property
    def r(self):
        """Euclidean distance from origin."""
        return (np.sum(self.c**2))**0.5

    @property
    def theta(self): 
        """Polar angle from x-axis."""
        if len(self.c) != 2:
            raise Exception('Property only applicable to 2-D Points')
        return np.arctan2(self.y, self.x)

    @property
    def theta_deg(self):
        return (180 / np.pi) * self.theta

    @staticmethod
    def _pdist(p1, p2, p=2):
        """p-norm distance for general p. Manhattan p = 1, Euclidean p = 2."""
        return (np.sum(np.abs(p1.c - p2.c)**p))**(1/p)

    def _make_dist(self, p):
        """Make a p-norm distance function of 2 arguments with parameter p."""
        return lambda x, y: self._pdist(x, y, p=p)

    def dist(self, p2, kind='euclidean'):
        """Calculate distance between self and second Point."""
        kinds = {'manhattan': self._make_dist(1),
                 'euclidean': self._make_dist(2)}
        return kinds[kind](self, p2)

    def __str__(self):
        return 'Point({}, {})'.format(self.x, self.y)

    def __repr__(self):
        return self.__str__()


def parse(line):
    """Convert string '123, 45\n' to tuple of integers (123, 45)."""
    data = line.rstrip()
    res = pat.match(data)
    x, y = int(res.group(1)), int(res.group(2))
    return Point((x, y))

filename = './data/input06.dat'
with open(filename, 'r') as file:
    coords = [parse(x) for x in file.readlines()]

# Convenience arrays
x, y, angles = np.array([(p.x, p.y, p.theta_deg) for p in coords]).T

# Brute force:
#  1. create integer grid that circumscribes max dimensions
#  2. classify grid points via 1-NN
#  3. count points labeled in each class
#  4. take maximum count, excluding convex hull of centroids

# xg, yg = 

#------------------------------------------------------------------------------ 
#        Plots
#------------------------------------------------------------------------------
fig = plt.figure(1)
fig.clf()
ax = fig.add_subplot(111)
sc = ax.scatter(x, y, c=angles, vmin=0, vmax=90)
# ax.scatter(x[:2], y[:2], marker='x', c='r', s=100)

cbar = plt.colorbar(sc)
cbar.ax.set_ylabel(r'$\theta$ [deg]')
ax.set_xlabel(r'$x$')
ax.set_ylabel(r'$y$')

plt.show()
#==============================================================================
#==============================================================================
