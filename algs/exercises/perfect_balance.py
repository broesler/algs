#!/usr/bin/env python3
# =============================================================================
#     File: perfect_balance.py
#  Created: 2020-02-20 22:52
#   Author: Bernie Roesler
#
"""
  Description: Insert items into a BST with "perfect" balance.
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


def is_balanced(t=None):
    """Return True if `t` is perfectly balanced."""
    return _is_balanced(t._root)


def _is_balanced(x=None):
    """Return True if subtree rooted at `x` is perfectly balanced."""
    if x is None:
        return True

    if (abs(BST._size(x.left) - BST._size(x.right)) < 2
       and _is_balanced(x.left)
       and _is_balanced(x.right)):
        return True

    return False


if __name__ == '__main__':
    import string
    from random import shuffle

    a = list(string.ascii_uppercase)
    shuffle(a)  # start with random list

    t = make_balanced_tree(a)
    print(t.level_order())
    assert(t.height == 5)
    # Make sure the tree is balanced
    assert(is_balanced(t))

# =============================================================================
# =============================================================================
