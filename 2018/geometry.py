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

def theta(x, y):
    return np.arctan2(y, x)

def theta_deg(x, y):
    return rad2deg(theta(x, y))

def poly_area(pts, signed=False):
    """
    Area of a simple 2D polygon.
    
    :param ndarray pts: shape (N, 2), array of polygon vertices, in order
    :param bool signed: if pts are CCW, area > 0, else area < 0.
    :returns: area of polygon
    :rtype: float
    """
    if pts.shape[1] != 2:
        raise Exception('poly_area only supports 2D points!')

    x, y = pts.T
    area = 0.5 * (  np.dot(x, np.roll(y, 1)) 
                  - np.dot(y, np.roll(x, 1)))
    return area if signed else np.abs(area)

def sort_by_x(points):
    return points[np.argsort(points[:, 0])]

def sort_by_y(points):
    return points[np.argsort(points[:, 1])]


class ConvexHull():
    def __init__(self, points, kind='orthogonal'):
        """Initialize convex hull with array of input points.

        :param ndarray points: shape (N, 2), array of input points
        """
        if points.shape[1] != 2:
            raise Exception('ConvexHull only supports 2D points!')
        self.points = points
        self.kind = kind
        self.vertices = self._vertices()

    def _vertices(self):
        vlist = list()
        # sort points by x
        pts = sort_by_x(self.points)
        # get four corners, merge lists
        return vlist

    def simplices(self):
        pass

#==============================================================================
#==============================================================================
