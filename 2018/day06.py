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

pat = re.compile(r'(\d+), (\d+)')

class Point():
    """Geometric point class."""
    def __init__(self, c=[], kind='cartesian'):
        """Create a Point object with given coordinates.

        :param array-like c: shape (n,), Cartesian coordinate vector
        :param str kind: 'cartesian', 'polar', etc. defines how input vector is
            used to define shorthand attributes.
        :returns: Point object
        :rtype: Point
        """
        if kind.lower() == 'cartesian':
            self.c = np.array(c)
        elif kind.lower() == 'polar':
            if len(c) != 2:
                raise Exception('Polar only applicable to 2-D Points')
            r = c[0]
            theta = c[1]
            self.c = self.pol2cart(r, theta)
            self.r = r
            self.theta = theta
        # elif kind.lower() == 'spherical', etc.
        else:
            raise Exception(f'Invalid kind {kind}')

    @property
    def dims(self):
        return self.c.size

    @staticmethod
    def pol2cart(r, theta):
        """Convert polar coordinates to Cartesian coordinates."""
        return np.array([r * np.cos(theta),
                         r * np.sin(theta)])

    #-------------------------------------------------------------------------- 
    #        Shorthand for 2D or 3D points
    #--------------------------------------------------------------------------
    @property
    def x(self):
        return self.c[0] if self.dims > 0 else None

    @x.setter
    def x(self, val):
        self.c[0] = val 

    @property
    def y(self):
        return self.c[1] if self.dims > 1 else None

    @y.setter
    def y(self, val):
        self.c[1] = val 

    @property
    def z(self):
        return self.c[2] if self.dims > 2 else None

    @z.setter
    def z(self, val):
        self.c[2] = val 

    #-------------------------------------------------------------------------- 
    #        Polar coors
    #--------------------------------------------------------------------------
    @property
    def r(self):
        """Euclidean distance from origin."""
        return (np.sum(self.c**2))**0.5

    @r.setter
    def r(self, val):
        """Assumes theta held constant."""
        theta = getattr(self, 'theta', 0)
        self.c = self.pol2cart(val, theta)

    @property
    def theta(self): 
        """Polar angle from x-axis."""
        if (self.dims != 2) and (self.dims != 3):
            raise Exception('Property only applicable to 2-D and 3-D Points')
        return np.arctan2(self.y, self.x)

    @theta.setter
    def theta(self, val):
        """Assumes r held constant."""
        if (self.dims != 2) and (self.dims != 3):
            raise Exception('Property only applicable to 2-D and 3-D Points')
        r = getattr(self, 'r', 1)
        self.c = self.pol2cart(r, val)

    @property
    def theta_deg(self):
        return (180 / np.pi) * self.theta

    @staticmethod
    def _pdist(c1, c2, p=2):
        """p-norm distance for general p. Manhattan p = 1, Euclidean p = 2."""
        return (np.sum(np.abs(c1 - c2)**p))**(1/p)

    def _make_dist(self, p):
        """Make a p-norm distance function of 2 arguments with parameter p."""
        return lambda a, b: self._pdist(a, b, p=p)

    def dist(self, p2, kind='euclidean'):
        """Calculate distance between self and second Point."""
        kinds = {'manhattan': self._make_dist(1),
                 'euclidean': self._make_dist(2)}
        func = kinds.get(kind.lower(), lambda x, y: f'Invalid kind {x}')
        return func(self.c, p2.c)

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
sc = ax.scatter(x, y, c=angles)
# ax.scatter(x[:2], y[:2], marker='x', c='r', s=100)

cbar = plt.colorbar(sc)
cbar.ax.set_ylabel(r'$\theta$ [deg]')
ax.set_xlabel(r'$x$')
ax.set_ylabel(r'$y$')

plt.show()
#==============================================================================
#==============================================================================
