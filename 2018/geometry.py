#!/Users/bernardroesler/anaconda3/envs/insight/bin/python3
#==============================================================================
#     File: geometry.py
#  Created: 2019-02-06 20:08
#   Author: Bernie Roesler
#
"""
  Description: Geometry objectcs and methods
"""
#==============================================================================

import numpy as np

#------------------------------------------------------------------------------ 
#        Utilities
#------------------------------------------------------------------------------
def rad2deg(theta):
    return (180 / np.pi) * theta

def deg2rad(theta_deg):
    return (np.pi / 180) * theta_deg

def pol2cart(r, theta):
    return np.array([r * np.cos(theta),
                     r * np.sin(theta)])

def cart2pol(x, y):
    return np.array([(x**2 + y**2)**0.5,
                     np.arctan2(y, x)])

#------------------------------------------------------------------------------ 
#        Classes
#------------------------------------------------------------------------------
class Point():
    """Geometric point class.

    Examples
    --------
    >>> origin = Point((0, 0))
    >>> origin.x, origin.y, origin.z
    (0.0, 0.0, None)
    >>> p = Point((3, 4))
    >>> p.x, p.y
    (3.0, 4.0)
    >>> p.r
    5.0
    >>> origin.dist(p)  # default Euclidean
    5.0
    >>> origin.dist(p, kind='manhattan')
    7.0
    >>> q = Point((1, 1))
    >>> q.r - np.sqrt(2)
    0.0
    >>> q.theta - np.pi/4
    0.0
    >>> q.theta_deg
    45.0
    """

    def __init__(self, c=list(), kind='cartesian'):
        """Create a Point object with given coordinates.

        :param array-like c: shape (n,), coordinate vector
        :param str kind: 'cartesian', 'polar', etc. defines how input vector is
            used to define shorthand attributes.
        :returns: Point object
        :rtype: Point
        """
        if kind.lower() == 'cartesian':
            self.c = np.array([float(x) for x in c])
        elif kind.lower() == 'polar':
            if len(c) != 2:
                raise Exception('Polar only applicable to 2-D Points')
            self.c = pol2cart(c[0], c[1])
        # elif kind.lower() == 'spherical', etc.
        else:
            raise Exception(f'Invalid kind {kind}')

    @property
    def dims(self):
        return self.c.size

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
    #        Polar coords
    #--------------------------------------------------------------------------
    @property
    def r(self):
        """Euclidean distance from origin."""
        return (np.sum(self.c**2))**0.5

    @r.setter
    def r(self, val):
        self.c = pol2cart(val, self.theta)

    @property
    def theta(self): 
        """Polar angle from x-axis."""
        if (self.dims != 2) and (self.dims != 3):
            raise Exception('Property only applicable to 2-D and 3-D Points')
        return np.arctan2(self.y, self.x)

    @theta.setter
    def theta(self, val):
        if (self.dims != 2) and (self.dims != 3):
            raise Exception('Property only applicable to 2-D and 3-D Points')
        self.c = pol2cart(self.r, val)

    @property
    def theta_deg(self):
        return rad2deg(self.theta)

    #-------------------------------------------------------------------------- 
    #        Distance
    #--------------------------------------------------------------------------
    @staticmethod
    def _pdist(a, b, p=2):
        """p-norm distance for general p. 

        :param array-like a: vector of coordinates of point 1
        :param array-like b: vector of coordinates of point 2
        :param float p: p-norm value, typically integer. Manhattan p = 1,
                        Euclidean p = 2.
        :returns d: distance between two points
        :rtype float:
        """
        return (np.sum(np.abs(a - b)**p))**(1/p)

    def _make_dist(self, p):
        """Make a p-norm distance function of 2 arguments with parameter p."""
        return lambda a, b: self._pdist(a, b, p=p)

    def dist(self, q, kind='euclidean'):
        """Calculate distance between self and second Point."""
        if self.dims != q.dims:
            raise Exception("Points must have same dimensionality! ({} != {})"\
                            .format(self.dims, q.dims))
        kinds = {'manhattan': self._make_dist(1),
                 'euclidean': self._make_dist(2)}
        func = kinds.get(kind.lower(), lambda x, y: f'Invalid kind {x}')
        return func(self.c, q.c)

    #-------------------------------------------------------------------------- 
    #        Utilities
    #--------------------------------------------------------------------------
    def __str__(self):
        return 'Point({}, {})'.format(self.x, self.y)

    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    import doctest
    doctest.testmod()

#==============================================================================
#==============================================================================
