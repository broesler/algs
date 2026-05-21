#!/usr/bin/env python3
#==============================================================================
#     File: dynamic_median.py
#  Created: 2020-02-19 14:25
#   Author: Bernie Roesler
#
"""
  Description: Solution to Exercise 2.4.30: Dynamic median-finding. 
    Design a data type that supports insert in logarithmic time, find the
    median in constant time, and delete the median in logarithmic time. 
    Hint: Use a min-heap and a max-heap.
"""
#==============================================================================

from copy import deepcopy as _deepcopy

from algs.basics import Collection, PriorityQueue as _PQ

class MedianPQ(Collection):
    """Iterable priority queue object, where priority is given to the median.

    A custom key function can be supplied to determine the sort order.

    Parameters
    ----------
    items : list of objects, optional
        Items to add to the queue.
    key : callable, optional
        Transformation function used in item comparison, *see* `sorted`.

    Attributes
    ----------
    size : int
        Number of items in queue.
    is_empty : bool
        True if `size == 0`
    """
    def __init__(self, items=list(), key=None):
        self._v = None  # the median item
        self._large = _PQ(kind='min')  # store items > self._v
        self._small = _PQ(kind='max')  # store items < self._v
        self._key = key or (lambda x: x)
        for k in items:
            self.enqueue(k)

    @property
    def size(self):
        if self._v is None:
            return 0
        else:
            return 1 + len(self._large) + len(self._small)

    def peek(self):
        """Look at first item in queue without dequeue-ing."""
        self._empty_check()
        return self._v

    def enqueue(self, k):
        """Add item to the queue in proper position."""
        if self.is_empty:
            self._v = k
            return

        if self._key(k) < self._key(self._v):
            # TODO abstract this shift operation to _shift_item(small, large)
            self._small.enqueue(k)
            if self._small.size > self._large.size:
                # shift values to the right
                self._large.enqueue(self._v)
                self._v = self._small.dequeue()
        elif self._key(k) > self._key(self._v):
            self._large.enqueue(k)
            if self._large.size > self._small.size:
                # shift values to the left
                self._small.enqueue(self._v)
                self._v = self._large.dequeue()
        else:  # k == self._v
            # choose side with fewer items
            if self._large.size < self._small.size:
                self._large.enqueue(k)
            else:
                self._small.enqueue(k)

    def dequeue(self):
        """Remove and return median item."""
        self._empty_check()
        out = self._v  # keep pointer to return item
        # Set median to value from queue with more items
        try:
            if self._large.size > self._small.size:
                self._v = self._large.dequeue()
            else:
                self._v = self._small.dequeue()
        except IndexError:
            self._v = None  # last item remaining
        return out

    def __str__(self):
        return str(list(self._small)[::-1] + [self._v] + list(self._large))

    # Iterator methods: make a copy because in-order iteration is destructive.
    def __iter__(self):
        self._pq_copy = _deepcopy(self)
        return self

    def __next__(self):
        try:
            return self._pq_copy.dequeue()
        except IndexError:
            raise StopIteration


if __name__ == '__main__':
    # TODO move to proper unit testing suite for package
    import string
    import numpy as np

    tests = fails = 0

    def should_be(a, b, name=None, verbose=False):
        """Test a condition."""
        global tests, fails
        tests += 1
        try:
            assert a == b
            if verbose:
                print(f"[{name}]: Got: {a}, Expected: {b}")
        except AssertionError as e:
            fails += 1
            print(f"[{name}]: Got: {a}, Expected: {b}")
            raise e

    # m = MedianPQ(string.ascii_uppercase[:11])
    # TODO test with, say, tuples as input to use key for sorting
    m = MedianPQ(range(11))
    should_be(m.is_empty, False)
    should_be(len(m), 11)
    should_be(m.peek(), 5)
    should_be(list(m), [5, 4, 6, 3, 7, 2, 8, 1, 9, 0, 10])

    # Summary
    if fails > 0:
        print(f"{fails}/{tests} tests failed")
    else:
        print(f"All {tests} tests passed!")






#==============================================================================
#==============================================================================
