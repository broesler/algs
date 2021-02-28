#!/usr/bin/env python3
# =============================================================================
#     File: tree_to_list.py
#  Created: 2020-03-10 22:15
#   Author: Bernie Roesler
#
"""
Description: *The great tree-list recursion problem*
    A binary search tree and a circular doubly linked list are conceptually
    built from the same type of nodes - a data field and two references to
    other nodes. Given a binary search tree, rearrange the references so that
    it becomes a circular doubly-linked list (in sorted order). Nick Parlante
    describes this as one of the neatest recursive pointer problems ever
    devised. 

    *Hint* create a circularly linked list `A` from the left subtree,
    a circularly linked list `B` from the right subtree, and make the root
    a one node circularly linked list. Then merge the three lists.

    See: <http://cslibrary.stanford.edu/109/TreeListRecursion.html>
"""
# =============================================================================

from algs import BST


def tree_to_list(t):
    """Reset the `left` and `right` pointers of the nodes of `t` to form
    a circular linked list in sorted order.
    """
    return _tree_to_list(t._root)


def _tree_to_list(x=None):
    """Reset the `left` and `right` pointers of the nodes of the subtree rooted
    at `x` to form a circular linked list in sorted order.
    """
    if x is None:
        return None

    # Recursively form lists from the subtrees
    A = _tree_to_list(x.left)
    B = _tree_to_list(x.right)

    # Turn root into single-node list
    x.left = x
    x.right = x

    # Merge the three lists
    A = _append(A, x)
    A = _append(A, B)

    return A


def _append(a, b):
    """Append circular linked list `b` onto `a`."""
    if a is None:
        return b
    if b is None:
        return a

    # Get pointers to the tails of the lists
    a_tail = a.left
    b_tail = b.left

    # Join the list s.t. b follows a
    _join(a_tail, b)
    _join(b_tail, a)

    return a


def _join(a, b):
    """Join circular linked list nodes `a` and `b`."""
    a.right = b
    b.left = a


if __name__ == '__main__':
    a = 'SEARCHEXAMPLE'
    t = BST(zip(a, range(len(a))))
    print(t.level_order())
    # A = tree_to_list(t)
    # x = A
    # while x is not None:
    #     print(x.right)
    #     if x.right is A:
    #         break

# =============================================================================
# =============================================================================
