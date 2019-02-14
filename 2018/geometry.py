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

def sort_by_x(points):
    return points[np.argsort(points[:, 0])]

def sort_by_y(points):
    return points[np.argsort(points[:, 1])]

def sort_by_xy(points):
    return points[np.lexsort((points[:, 1], points[:, 0]))]

def argsort_by_xy(points):
    return np.lexsort((points[:, 1], points[:, 0]))

#------------------------------------------------------------------------------ 
#        Algorithm for Orthogonal Convex Hull
#------------------------------------------------------------------------------
# From <https://stackoverflow.com/questions/32496421/orthogonal-hull-algorithm>
#
# 1. Start constructing upper hull from the leftmost point (uppermost among such
#    if there are many). Add this point to a list.
# 2. Find the next point: among all the points with both coordinates strictly
#    greater than of the current point, choose the one with minimal
#    x coordinate. Add this point to your list and continue from it.
# 3. Continue adding points in step 2 as long as you can.
# 4. Repeat the same from the rightmost point (uppermost among such), but going
#    to the left. I.e. each time choose the next point with greater y, less x,
#    and difference in x must be minimal.
# 5. Merge the two lists you got from steps 3 and 4, you got upper hull.
# 6. Do the same steps 1-5 for lower hull analogously.
# 7. Merge the upper and lower hulls found at steps 5 and 6.
#
# In order to find the next point quickly, just sort your points by
# x coordinate. For example, when building the very first right-up chain, you
# sort by x increasing. Then iterate over all points. For each point check if
# its y coordinate is greater than the current value. If yes, add the point to
# the list and make it current.
#
# EDIT: The description above only shows how to trace the main vertices of the
# hull. If you want to have a full rectilinear polygon (with line segments
# between consecutive points), then you have to add an additional point to your
# chain each time you find next point. For example, when building the right-up
# chain, if you find a point (x2, y2) from the current point (x1, y1), you have
# to add (x2, y1) and (x2, y2) to the current chain list (in this order).

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

    Attributes
    ----------
    points : (M, 2) ndarray 
        array of input points

    vertices : (N, 2) ndarray
        Indices of points forming the vertices of the convex hull. For 2-D
        convex hulls, the vertices are in counterclockwise order.

    """
    def __init__(self, points, kind=''):
        self.points = np.asarray(points)
        if self.points.shape[1] != 2:
            raise Exception('ConvexHull only supports 2D points!')
        self.points = np.asarray(points)
        self.kind = kind
        self.vertices = self._vertices()

    def _vertices(self):
        vlist = list()
        # TODO use only indices of points so we don't have to copy that array
        pts = sort_by_xy(self.points)
        upper_left = pts[pts[:, 0] == pts[0, 0]][-1]
        vlist.append(upper_left)
        curr = vlist[-1]
        for p in pts:
            if p[1] > curr[1]:
                vlist.append(p)
                curr = vlist[-1]

        return np.asarray(vlist)

    def simplices(self):
        pass

#==============================================================================
#==============================================================================
