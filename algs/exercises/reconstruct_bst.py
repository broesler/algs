#!/usr/bin/env python3
# =============================================================================
#     File: reconstruct_bst.py
#  Created: 2021-03-01 17:17
#   Author: Bernie Roesler
#
"""
  Description: Given a pre-order traversal of a BST, reconstruct the tree.
    See: <https://algs4.cs.princeton.edu/32bst/> for more info.
"""
# =============================================================================

from algs.search import BST

# Test known example
st = BST.fromkeys(list('SEARCHEXAMPLE'))
assert st.pre_order() == list('SEACRHMLPX')  # compute manually

# Test reconstructed examples
rst = BST.fromkeys(st.pre_order())
assert rst.pre_order() == st.pre_order()
assert rst == st

st = BST.fromkeys(list('EASYQUESTION'))
rst = BST.fromkeys(st.pre_order())
assert rst.pre_order() == st.pre_order()
assert rst == st

# =============================================================================
# =============================================================================
