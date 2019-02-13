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
    
    Parameters
    ----------
    pts : (M, 2) array_like 
        array of M, 2-D polygon vertices, in order
    signed : bool
        if pts are CCW, area > 0, else area < 0.

    Returns
    -------
    area : float
        area of polygon
    """
    if pts.shape[1] != 2:
        raise Exception('poly_area only supports 2D points!')

    x, y = np.asarray(pts).T
    area = 0.5 * (  np.dot(x, np.roll(y, 1)) 
                  - np.dot(y, np.roll(x, 1)))
    return area if signed else np.abs(area)

class ConvexHull():
    """
    Convex hull of array of input points.

    Parameters
    ----------
    points : (M, 2) array_like 
        array of input points
    kind : str
        'orthogonal' -- orthogonal convex hull
        '' -- Euclidean convex hull
    """
    def __init__(self, points, kind=''):
        self.points = np.asarray(points)
        if self.points.shape[1] != 2:
            raise Exception('ConvexHull only supports 2D points!')
        self.kind = kind

    def vertices(self):
        pass

    def simplices(self):
        pass

#==============================================================================
#==============================================================================
