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

def sort_by_xy(points, x_ascending=True, y_ascending=True):
    """Sort array of points by x, then y."""
    return points[argsort_by_xy(points)]

def argsort_by_xy(points, x_ascending=True, y_ascending=True):
    """Sort array of points by x, then y; return indices."""
    _rev_x = None if x_ascending else -1

    if x_ascending:
        _rev_y = None if y_ascending else -1  # y works as expected
    else:
        _rev_y = -1 if y_ascending else None  # y role is reversed

    rev_x = slice(None, None, _rev_x)
    rev_y = slice(None, None, _rev_y)

    # [rev_x] must go outside the final sort
    return np.lexsort((points[:, 1][rev_y], points[:, 0]))[rev_x]

#------------------------------------------------------------------------------ 
#        Algorithm for Orthogonal Convex Hull
#------------------------------------------------------------------------------
# From <https://stackoverflow.com/questions/32496421/orthogonal-hull-algorithm>
# TODO: If you want to have a full rectilinear polygon (with line segments
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
        Array of points forming the N vertices of the convex hull. For 2-D
        convex hulls, the vertices are in counterclockwise order.

    """
    def __init__(self, points, kind=''):
        self.points = np.asarray(points)
        if self.points.shape[1] != 2:
            raise Exception('ConvexHull only supports 2D points!')
        self.points = np.asarray(points)
        self.kind = kind
        self.vertices = self._vertices()

    # def _ortho_search(self, x_ascending=True, y_ascending=True):
    #     """Find orthogonal convex hull quarters."""
    #     vlist = list()  # list of indices
    #     ind = argsort_by_xy(self.points)  # point indices sorted by x, then y
    #     return np.asarray(vlist)

    def _vertices(self):
        vlist = list()  # list of indices
        ind = argsort_by_xy(self.points)  # point indices sorted by x, then y

        # Top left to top right
        #   **Increasing x, increasing y**
        # Get the index of the point with the largest y-value out of the points
        # with the smallest x-value
        upper_left = np.flatnonzero(   self.points[ind][:, 0] 
                                    == self.points[ind][0, 0])[-1]
        vlist.append(upper_left)
        curr = vlist[0]
        for i in ind:
            if self.points[i, 1] > self.points[curr, 1]:
                vlist.append(i)
                curr = vlist[-1]

        # Top left to bottom right
        #   **Increasing x, decreasing y**
        import ipdb; ipdb.set_trace()
        curr = vlist[0]
        for i in ind:
            if self.points[i, 1] < self.points[curr, 1]:
                vlist.append(i)
                curr = vlist[-1]

        # Top right to top left
        #   **Decreasing x, increasing y**
        # Get the index of the point with the largest y-value out of the points
        # with the largest x-value
        upper_right = np.flatnonzero(   self.points[ind][:, 0] 
                                     == self.points[ind][-1, 0])[-1]
        vlist.append(upper_right)
        ur_idx = len(vlist)-1  # current end of list index
        curr = vlist[-1]
        for i in ind[::-1]:
            if self.points[i, 1] > self.points[curr, 1]:
                vlist.append(i)
                curr = vlist[-1]

        # Top right to bottom left
        #   **Decreasing x, decreasing y**
        curr = vlist[ur_idx]
        for i in ind[::-1]:
            if self.points[i, 1] < self.points[curr, 1]:
                vlist.append(i)
                curr = vlist[-1]

        return np.asarray(vlist)

    def simplices(self):
        pass

#==============================================================================
#==============================================================================
