#!/usr/bin/env python3
# =============================================================================
#     File: special.py
#  Created: 2022-06-07 17:04
#   Author: Bernie Roesler
#
"""
Menagerie of classes that use symbol tables, but don't quite fit in elsewhere.
"""
# =============================================================================

from algs.basics import Queue
from algs.search import HashSet


# Exercise 3.5.28
class Uniqueue(Queue):
    """A queue, except an element may only be inserted once."""

    def __init__(self, items=None):
        items = items or []
        self._st = HashSet()
        super().__init__()
        for item in items:
            self.enqueue(item)

    def enqueue(self, item):
        if item not in self._st:
            self._st.add(item)
            super().enqueue(item)


if __name__ == '__main__':
    keys = list('SEARCHEXAMPLE')
    q = Uniqueue(keys)
    print(q)

# =============================================================================
# =============================================================================
