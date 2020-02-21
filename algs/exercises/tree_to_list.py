#!/usr/bin/env python3
# =============================================================================
#     File: tree_to_list.py
#  Created: 2020-02-19 21:44
#   Author: Bernie Roesler
#
"""
  Description: 
    **The great tree-list recursion problem.** A binary search tree and
    a circular doubly linked list are conceptually built from the same type of
    nodes - a data field and two references to other nodes. Given a binary
    search tree, rearrange the references so that it becomes a circular
    doubly-linked list (in sorted order). Nick Parlante describes this as 
    [one of the neatest recursive pointer problems ever
    devised](http://cslibrary.stanford.edu/109/TreeListRecursion.html).

    *Hint:* create a circularly linked list A from the left subtree,
    a circularly linked list B from the right subtree, and make the root a one
    node circularly linked list. Then merge the three lists.
"""
# =============================================================================

# =============================================================================
# =============================================================================
