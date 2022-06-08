#!/usr/bin/env python3
# =============================================================================
#     File: adt.py
#  Created: 2022-06-08 09:10
#   Author: Bernie Roesler
#
"""
Abstract data types (ADTs) for use in exercises.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np


class Point2D():
    """A point in the Cartesian x-y plane.

    Attributes
    ----------
    x, y : float
        The Cartesian coordinates.
    r, theta : float
        The polar coordinates.
    """

    def __init__(self, x, y):
        self.x = 0 if x == 0 else x  # correct for -0.0 input
        self.y = 0 if y == 0 else y

    @property
    def r(self):
        """The radius in polar coordinates."""
        return (self.x*self.x + self.y*self.y)**0.5

    @property
    def theta(self):
        """The angle in polar coordinates, between -π and π."""
        return np.arctan2(self.y, self.x)

    def dist_to(self, other):
        """Return the Euclidean distance from this point to `other`."""
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx*dx + dy*dy)**0.5

    def angle_to(self, other):
        """Return the angle between this point and `other`."""
        dx = self.x - other.x
        dy = self.y - other.y
        return np.arctan2(dy, dx)

    # ------------------------------------------------------------------------- 
    #         Comparators
    # -------------------------------------------------------------------------
    # Use these methods with `sorted(points, key=Point2D.X_ORDER)`
    @staticmethod
    def X_ORDER(p):
        return p.x

    @staticmethod
    def Y_ORDER(p):
        return p.y

    @staticmethod
    def R_ORDER(p):
        return p.r

    @staticmethod
    def THETA_ORDER(p):
        return p.theta

    def DIST_TO_ORDER(self, p):
        """Compare points by their distance to this point."""
        return self.dist_to(p)

    def ATAN2_ORDER(self, p):
        """Compare points by their angle with this point, in -π to π."""
        return self.angle_to(p)

    # ------------------------------------------------------------------------- 
    #         Plotting
    # -------------------------------------------------------------------------
    def draw(self, ax=None, **kwargs):
        """Plot the point in the specified axes."""
        if ax is None:
            ax = plt.gca()
        ax.scatter(self.x, self.y, **kwargs)

    def draw_to(self, other, ax=None, **kwargs):
        """Draw a line between this point and the other."""
        if ax is None:
            ax = plt.gca()
        ax.plot((self.x, other.x), (self.y, other.y), **kwargs)

    # ------------------------------------------------------------------------- 
    #         Internals
    # -------------------------------------------------------------------------
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.x == other.x) and (self.y == other.y)

    def __hash__(self):
        return 31*hash(self.x) + hash(self.y)

    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f})"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"


if __name__ == "__main__":
    import time
    # Generate N random points in the unit square
    rng = np.random.default_rng(seed=565656)
    N = 5
    points = []
    for i in range(N):
        points.append(Point2D(*rng.random(2)))

    x0, y0 = 0.1, 0.2
    p0 = Point2D(x0, y0)
    points = sorted(points, key=p0.DIST_TO_ORDER)

    fig = plt.figure(1, clear=True, tight_layout=True)
    ax = fig.add_subplot()
    p0.draw(ax, c='C3')
    for i, p in enumerate(points):
        # p.draw(ax, c='k')
        ax.text(p.x, p.y, f"{i}", ha='left', va='bottom')
        p0.draw_to(p, ax=ax)
        fig.canvas.draw()

    ax.set(xlabel='x', xlim=(0, 1),
           ylabel='y', ylim=(0, 1),)
    ax.grid(True)
    plt.show()

# =============================================================================
# =============================================================================
