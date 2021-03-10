#!/usr/bin/env python3
# =============================================================================
#     File: test_balanced_tree.py
#  Created: 2021-03-09 18:47
#   Author: Bernie Roesler
#
"""
  Description: Tests specific to balanced trees.
"""
# =============================================================================

import numpy as np

from algs.search import RedBlackBST
from algs.tests.helpers import should_be, err_test

# TODO write Pytest classes/functions
# Ex 3.1.29 (and then some!)

rng = np.random.default_rng(seed=565656)

# Prepare test data
test_str = 'SEARCHEXAMPLE'
test_set = set(test_str)
data = [(c, i) for i, c in enumerate(test_str)]
data_set = data.copy()
data_set.remove(('E', 1))
data_set.remove(('A', 2))
data_set.remove(('E', 6))

ST = RedBlackBST
# t = ST(data)

# # Test insertion without rotates
# t = RedBlackBST.fromkeys(list('SAX'))
# expected = [('S', 3, 1), ('A', 1, 0), ('X', 1, 0)]
# node_attrs = t.level_order(op=lambda x: (x.key, x.N, x.height))
# should_be(node_attrs, expected)

# # Test left rotation of right-leaning red link
# t = RedBlackBST.fromkeys(list('ES'))
# expected = [('S', 2, 1), ('E', 1, 0)]
# node_attrs = t.level_order(op=lambda x: (x.key, x.N, x.height))
# should_be(node_attrs, expected)

# # Test right rotation of two red links
# t = RedBlackBST.fromkeys(list('SEA'))
# expected = [('E', 3, 1), ('A', 1, 0), ('S', 1, 0)]
# node_attrs = t.level_order(op=lambda x: (x.key, x.N, x.height))
# should_be(node_attrs, expected)

# Test attributes of (somewhat) random tree
keys = list('MERCLPXAHS')
Ns   = [10, 5, 4, 2, 2, 1, 2, 1, 1, 1]
hs   = [ 3, 2, 2, 1, 1, 0, 1, 0, 0, 0]
# ipls = list(zip(list('MERCLPXAHS'), [3, 2, 2, 1, 1, 0, 1, 0, 0, 0]))

t = ST(data)
node_attrs = t.level_order(op=lambda x: (x.key, x.N))
should_be(node_attrs, list(zip(keys, Ns)))

# node_attrs = t.level_order(op=lambda x: (x.key, x.height))
# should_be(node_attrs, list(zip(keys, hs)))

# should_be(t.height_r(), 3)  # recursive method
# should_be(t.height, 3)      # Node attribute method
# should_be(t.isBST(), True)
# should_be(t.internal_path_length_r(), 26)
# should_be(t.internal_path_length, 26)
# del t['H']  # remove node with single child
# should_be(t.height_r(), 4)  # recursive method
# should_be(t.height, 4)      # Node attribute method
# should_be(t.internal_path_length, 20)
# t = ST(data, cache=cache)
# t['G'] = 6
# should_be(t.internal_path_length, 30)
# del t['H']  # remove node with two children
# should_be(t.internal_path_length, 25)

# Test height of each node
# t = ST(data, cache=cache)
# t_heights = t.level_order(op=lambda x: (x.key, x.height))
# should_be(t_heights, heights)

# =============================================================================
# =============================================================================
