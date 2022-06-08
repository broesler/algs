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

import re
import matplotlib.pyplot as plt
import numpy as np


# ----------------------------------------------------------------------------- 
#         Geometric
# -----------------------------------------------------------------------------
class Point2D:
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
    # Use these methods as `sorted(points, key=Point2D.X_ORDER)`,
    # in lieu of writing `sorted(points, key=lambda p: p.x)`)`.
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


class Interval1D:
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


class Interval2D:
    """A 2D interval aligned with the x- and y-axes."""

    def __init__(self, x0, y0, x1=None, y1=None):
        """
        Parameters
        ----------
        x0, y0 : float or Interval1D
            If x1, y1 are None, these arguments are expected to be Intervals
            defining the x- and y-limits of the box.
        x1, y1 : float, optional
            If given, they are treated as the upper limits of the x- and y-
            intervals of the box.
        """
        if x1 is None and y1 is None:
            assert isinstance(x0, Interval1D) and isinstance(y0, Interval1D)
            self.x = x0
            self.y = y0
        else:
            self.x = Interval1D(x0, x1)
            self.y = Interval1D(y0, y1)

    @property
    def area(self):
        """Area of the 2D interval (box)."""
        return self.x.length * self.y.length

    def __contains__(self, p):
        """Return True if point `p` is inside the box."""
        return (p.x in self.x) and (p.y in self.y)

    def contains(self, p):
        return self.__contains__(p)

    def intersects(self, other):
        """Return True if this interval intersects `other`."""
        return self.x.intersects(other.x) and self.y.intersects(other.y)

    # Plots
    def draw(self, ax=None, facecolor='none', **kwargs):
        """Plot the box in the specified axes."""
        if ax is None:
            ax = plt.gca()
        rect = plt.Rectangle((self.x.lo, self.y.lo),
                             width=self.x.length,
                             height=self.y.length,
                             zorder=3,  # plot above grid
                             facecolor=facecolor,
                             **kwargs)
        ax.add_patch(rect)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.x == other.x) and (self.y == other.y)

    def __hash__(self):
        return 31*hash(self.x) + hash(self.y)

    def __str__(self):
        return str(self.x) + ' x ' + str(self.y)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"


# ----------------------------------------------------------------------------- 
#         Information Processing
# -----------------------------------------------------------------------------
class Date:
    """A data type to represent the day, month, and year."""
    DAYS = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    pat = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")

    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            month, day, year = self.pat.findall(args[0])[0]
        elif len(args) > 1:
            month, day, year = args[:3]
        else:
            month, day, year = kwargs['month'], kwargs['day'], kwargs['year']
        self.month = int(month)
        self.day = int(day)
        self.year = int(year)
        self.validate(self.month, self.day, self.year)

    def validate(self, month, day, year):
        if not (1 <= month <= 12):
            raise ValueError(f"{month} must be between 1 and 12.")
        if not (1 <= day <= self.DAYS[month-1]):
            raise ValueError(day, 
                             f"There are only {self.DAYS[month-1]} days in {month=}!")
        if month == 2 and day == 29 and not self.is_leap_year(year):
            raise ValueError(f"{month}/{day}/{year} is not a leap year!")

    @staticmethod
    def is_leap_year(year):
        if year % 400 == 0:
            return True
        if year % 100 == 0:
            return False
        return year % 4 == 0

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.month == other.month 
                and self.day == other.day
                and self.year == other.year)

    def _compare_to(self, other):
        """Use old-school compare function internally for less code."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        if self.year < other.year:
            return -1
        elif self.year > other.year:
            return 1
        # years are equal
        if self.month < other.month:
            return -1
        elif self.month > other.month:
            return 1
        # years and months are equal
        if self.day < other.day:
            return -1
        elif self.day > other.day:
            return 1
        else:
            return 0

    def __lt__(self, other):
        return self._compare_to(other) < 0

    def __le__(self, other):
        return self._compare_to(other) <= 0

    def __gt__(self, other):
        return self._compare_to(other) > 0

    def __ge__(self, other):
        return self._compare_to(other) >= 0

    def __hash__(self):
        return self.day + 31*self.month + 31*12*self.year

    def __str__(self):
        return f"{self.month}/{self.day}/{self.year}"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"


class Transaction:
    """A class representing a transaction with a client."""
    
    def __init__(self, who, when, amount):
        assert isinstance(when, Date)
        assert not (np.isnan(amount) and np.isinf(amount))
        self.who = who
        self.when = when
        self.amount = amount

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.who == self.who
                and self.when == self.when
                and self.amount == self.amount)

    def __lt__(self, other):
        return self.amount < other.amount

    def __le__(self, other):
        return self.amount <= other.amount

    def __gt__(self, other):
        return self.amount > other.amount

    def __ge__(self, other):
        return self.amount >= other.amount

    # Comparators
    @staticmethod
    def WHO_ORDER(t):
        return t.who

    @staticmethod
    def WHEN_ORDER(t):
        return t.when

    @staticmethod
    def AMOUNT_ORDER(t):
        return t.amount

    def __hash__(self):
        h = 1
        h = 31*h + hash(self.who)
        h = 31*h + hash(self.when)
        h = 31*h + hash(self.amount)
        return h

    def __str__(self):
        return f"{self.who:10s} {str(self.when):10s} {self.amount:+8.2f}"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"


if __name__ == "__main__":
    # Make a date
    d0= Date('4/16/1990')
    d1 = Date(4, 16, 1990)
    assert d0 == d1
    assert d0 < Date('6/8/2022')
    assert d0 > Date('1/1/1990')

    # Make a transaction
    t0 = Transaction('Turing', Date('6/17/1990'), 644.08)
    t1 = Transaction('Knuth', Date('6/14/1999'), 288.34)
    print(t0)
    print(t1)
    assert t0 == t0
    assert t0 > t1

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

    i2 = Interval2D(i0, i1)
    i3 = Interval2D(0.6, 0.5, 0.8, 0.8)
    assert Point2D(0.2, 0.4) in i2

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
    i2.draw(edgecolor='C3', lw=2)
    i3.draw(edgecolor='C4', lw=2)

    ax.set(xlabel='x',
           ylabel='y',)
    ax.set_xlim(right=1)
    ax.set_ylim(top=1)
    ax.grid(True)

    plt.show()

# =============================================================================
# =============================================================================
