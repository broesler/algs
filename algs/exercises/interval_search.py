#!/usr/bin/env python3
# =============================================================================
#     File: interval_search.py
#  Created: 2022-06-10 00:31
#   Author: Bernie Roesler
#
"""
Exercise 3.5.24: Non-overlapping interval search for a point. Given a list of
non-overlapping intervals, find which one contains the query point.

Ex. [1643-2033, 5532-7643, 8999-10332, 5666653-5669321]
query(9122) == 3 
query(8122) == None
"""
# =============================================================================

from algs.adt import Interval1D
from algs.search import ST


class IntervalSearch():

    def __init__(self, ints):
        # Store intervals by their high value.
        self._st = ST()
        for i in ints:
            self._st[i.hi] = i


    def query(self, q):
        """Return the interval containing the query point `q`."""
        # Rank the query point among `hi` values to determine the interval in
        # which to search.
        x = self._st[self._st.select(self._st.rank(q))]
        return x if x.contains(q) else None


if __name__ == "__main__":
    ints = [Interval1D(1643, 2033),
            Interval1D(5532, 7643),
            Interval1D(8999, 10332),
            Interval1D(5666653, 5669321)]

    st = IntervalSearch(ints)
    assert st.query(9122) == ints[2]
    assert st.query(8122) is None


# =============================================================================
# =============================================================================
