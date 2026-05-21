#!/usr/bin/env python3
# =============================================================================
#     File: ringbuffer.py
#  Created: 2022-05-27 16:52
#   Author: Bernie Roesler
#
"""
Exercise 1.3.39 Implement a ring buffer of fixed size N.
"""
# =============================================================================

from algs.basics import Collection, Queue


# Exercise 1.3.39
class RingBuffer(Collection):
    """Implements a ring buffer of fixed size. If the buffer is full and an
    enqueue operation is performed, the oldest item is overwritten.

    Parameters
    ----------
    M : int
        The number of slots in the buffer.

    Attributes
    -------
    M : int
        The total number of slots in the buffer.
    size : int
        The number of items currently stored in the buffer.
    """

    def __init__(self, M, items=None):
        self.M = M
        self.N = 0
        self._items = M*[None]
        self._first = 0  # pointers to the first and last elements
        self._last = 0
        self._p = 0      # pointer for iteration
        items = items or []
        for x in items:
            self.enqueue(x)

    @property
    def size(self):
        return self.N

    @property
    def is_full(self):
        return self.M == self.N

    def enqueue(self, k):
        """Add an item to the buffer."""
        if self.is_full:
            self._first = (self._first + 1) % self.M
        self._items[self._last] = k
        self._last = (self._last + 1) % self.M  # circular, feeling the flow
        self.N = min(self.M, self.N + 1)        # allow for overwrites

    def dequeue(self):
        """Remove the oldest item from the buffer."""
        self._empty_check()
        v = self._items[self._first]
        self._items[self._first] = None
        self._first = (self._first + 1) % self.M
        self.N -= 1
        return v

    def peek(self):
        """Return the least recent item added without dequeuing."""
        return self._items[self._first]

    # When full, self._first == self._last, so raise a flag the first time
    def __iter__(self):
        self._p = self._first
        self._STOP = False
        return self

    def __next__(self):
        v = self._items[self._p]
        if self._p == self._last and self._STOP:
            raise StopIteration
        else:
            self._STOP = True
            self._p = (self._p + 1) % self.M
            return v


if __name__ == '__main__':
    q = RingBuffer(10, list('Hello'))
    assert q.N == 5
    assert q._first == 0
    assert q._last == 5
    print(q._items)
    print(q)  # iterate through partial queue

    # Fill and overwrite the queue by 1
    for c in 'World!':
        q.enqueue(c)
    assert q.is_full
    print(q._items)
    print(q)  # iterate through full queue

    assert q.dequeue() == 'e'
    print(q._items)
    print(q)
    assert q._first == 2
    assert q._last == 1

# =============================================================================
# =============================================================================
