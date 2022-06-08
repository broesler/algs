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

    # Comparators
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

    # Plotting
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

    # NOTE use np.isclose() here?
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


class Interval1D():
    """An interval along a single dimension, inclusive of its endpoints."""

    def __init__(self, lo, hi):
        self.lo = 0 if lo == 0 else lo  # avoid -0.0 issue
        self.hi = 0 if hi == 0 else hi

    @property
    def length(self):
        return self.hi - self.lo

    def __len__(self):
        return self.length

    def __contains__(self, x):
        """Return True if the interval contains the point `x`."""
        return self.lo <= x <= self.hi

    def contains(self, x):
        return self.__contains__(x)

    def intersects(self, other):
        """Return True if this interval intersects `other`."""
        return not ((self.hi < other.lo) or (other.hi < self.lo))

    # Comparators
    @staticmethod
    def MIN_ORDER(x):
        return x.lo

    @staticmethod
    def MAX_ORDER(x):
        return x.hi

    @staticmethod
    def LEN_ORDER(x):
        return x.length

    # Plots
    def draw(self, ax=None, marker_height=0.02, **kwargs):
        """Draw the interval along the x-axis of `ax`."""
        if ax is None:
            ax = plt.gca()
        ax.errorbar((self.lo, self.hi), (0, 0), yerr=marker_height, **kwargs)

    # Internals
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.lo == other.lo) and (self.hi == other.hi)

    def __hash__(self):
        return 31*hash(self.lo) + hash(self.hi)

    def __str__(self):
        return f"[{self.lo}, {self.hi}]"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"


if __name__ == "__main__":
    # Generate N random points in the unit square
    rng = np.random.default_rng(seed=565656)
    N = 5
    points = []
    for i in range(N):
        points.append(Point2D(*rng.random(2)))

    x0, y0 = 0.1, 0.2
    p0 = Point2D(x0, y0)
    points = sorted(points, key=p0.DIST_TO_ORDER)

    # Make two intervals
    i0 = Interval1D(0.1, 0.4)
    i1 = Interval1D(0.3, 0.5)
    assert i0.intersects(i1)
    assert 0.2 in i0
    assert 0.45 not in i0
    assert 0.45 in i1

    fig = plt.figure(1, clear=True, tight_layout=True)
    ax = fig.add_subplot()
    p0.draw(ax, c='C3')
    for i, p in enumerate(points):
        # p.draw(ax, c='k')
        ax.text(p.x, p.y, f"{i}", ha='left', va='bottom')
        p0.draw_to(p, ax=ax)
        fig.canvas.draw()
    i0.draw(c='C0')
    i1.draw(c='C2')

    ax.set(xlabel='x',
           ylabel='y',)
    ax.set_xlim(right=1)
    ax.set_ylim(top=1)
    ax.grid(True)
    plt.show()

# =============================================================================
# =============================================================================
