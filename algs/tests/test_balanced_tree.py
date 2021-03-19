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

import pytest

from algs.search import RedBlackBST
from algs.tests.test_search import data, t


class TestRotations:
    def test_insert_no_rotate(self):
        t = RedBlackBST.fromkeys(list('SAX'))
        expected = [('S', 3, 1), ('A', 1, 0), ('X', 1, 0)]
        assert t.level_order(op=lambda x: (x.key, x.N, x.height)) == expected

    def test_left_rotate(self):
        t = RedBlackBST.fromkeys(list('ES'))
        expected = [('S', 2, 1), ('E', 1, 0)]
        assert t.level_order(op=lambda x: (x.key, x.N, x.height)) == expected

    def test_right_rotate(self):
        t = RedBlackBST.fromkeys(list('SEA'))
        expected = [('E', 3, 1), ('A', 1, 0), ('S', 1, 0)]
        assert t.level_order(op=lambda x: (x.key, x.N, x.height)) == expected


@pytest.mark.parametrize('ST', [RedBlackBST])
def test_node_updates(self, t):
    keys = list('MERCLPXAHS')
    Ns = [10, 5, 4, 2, 2, 1, 2, 1, 1, 1]
    hs = [3, 2, 2, 1, 1, 0, 1, 0, 0, 0]
    # ipls = []
    assert t.level_order(op=lambda x: (x.key, x.N)) == list(zip(keys, Ns))
    assert t.level_order(op=lambda x: (x.key, x.height)) == list(zip(keys, hs))
    # assert t.level_order(op=lambda x: (x.key, x.ipl)) == list(zip(keys, ipls))


# Interactive test setup
if __name__ == '__main__':
    EXPECT_STR = 'SEARCHEXAMPLE'
    data = list((c, i) for i, c in enumerate(EXPECT_STR))
    st = RedBlackBST(data)

# =============================================================================
# =============================================================================
