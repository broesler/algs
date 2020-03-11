#!/usr/bin/env python3
# =============================================================================
#     File: perfect_balance.py
#  Created: 2020-02-20 22:52
#   Author: Bernie Roesler
#
"""
  Description: Insert items into a BST with "perfect" balance. Exercise 3.2.25.
"""
# =============================================================================

from algs.search import BST
from algs.sort import qsort


def make_balanced_tree(a):
    """Return a perfectly balanced BST of the items in `a`."""
    return _make_balanced_tree(qsort(a), 0, len(a)-1)


def _make_balanced_tree(a, lo, hi, t=None):
    """Recursively insert the median of the sorted iterable `a` into `t`.

    Parameters
    ----------
    a : list-like
        iterable of items to insert into the tree
    lo : int
        minimum index from which to find the median
    hi : int
        maximum index from which to find the median
    t : BST-like, optional, default `algs.search.BST`
        Mapping object into which to insert items. Intended for a binary search
        tree object.

    Returns
    -------
    t : BST
        Balanced binary search tree of the items in `a`.
    """
    if t is None:
        t = BST()
    if hi < lo:
        return t
    mid = (lo + hi) // 2
    t[a[mid]] = mid
    _make_balanced_tree(a, lo, mid - 1, t)
    _make_balanced_tree(a, mid + 1, hi, t)
    return t

if __name__ == '__main__':
    a = 'SEARCHX'
    t = make_balanced_tree(a)
    assert(t.is_balanced())  # make sure the tree is balanced
    assert(t.level_order() == list('HCSAERX'))  # See Algorithms text p. 403
    # print(t.level_order())

# =============================================================================
# =============================================================================
