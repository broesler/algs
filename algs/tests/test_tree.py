#!/usr/bin/env python3
# =============================================================================
#     File: test_tree.py
#  Created: 2021-04-15 14:00
#   Author: Bernie Roesler
#
"""
  Description:
"""
# =============================================================================

import pytest

from algs.search import BST, ThreadedST, ThreadedST_nr
from algs.tests.test_search import (data, t, expect_set,
                                    ORDERED_STS, BALANCED_TREES)


# -----------------------------------------------------------------------------
#         Test BST structure
# -----------------------------------------------------------------------------
@pytest.mark.parametrize('ST', set([x for x in ORDERED_STS if issubclass(x, BST)])
                               - BALANCED_TREES)
class TestBST:
    @staticmethod
    @pytest.fixture
    def heights():
        # Binary Search Tree:
        #  height depth
        #  5      0           S
        #                    / \
        #  4      1         E   X
        #                /    \
        #  3      2     A      R
        #                \    /
        #  2      3       C  H
        #                     \
        #  1      4            M
        #                     / \
        #  0      5          L   P
        return list(zip(list('SEXARCHMLP'), [5, 4, 0, 1, 3, 0, 2, 1, 0, 0]))
        # depths  = list(zip(list('SEXARCHMLP'), [0, 1, 1, 2, 2, 3, 3, 4, 5, 5]))

    def test_construction(self, t):
        assert t.isBST()
        # TODO test for each failure mode

    def test_orders(self, t):
        assert t.pre_order() ==   list('SEACRHMLPX')
        assert t.in_order() ==    list('ACEHLMPRSX')
        assert t.post_order() ==  list('CALPMHREXS')
        assert t.level_order() == list('SEXARCHMLP')

    def test_height(self, t, heights):
        assert t.height_r() == 5
        assert t.height == 5
        # Test height of each node individually
        t_heights = t.level_order(op=lambda x: (x.key, x.height))
        assert t_heights == heights
        del t['H']  # remove node with single child
        assert t.height_r() == 4
        assert t.height == 4

    def test_ipl_delete(self, t):
        assert t.internal_path_length_r() == 26
        assert t.internal_path_length == 26
        del t['H']  # remove node with single child
        assert t.internal_path_length == 20

    def test_ipl_insert(self, t):
        t['G'] = 6
        assert t.internal_path_length_r() == 30
        assert t.internal_path_length == 30
        del t['H']  # remove node with two children
        assert t.internal_path_length_r() == 25
        assert t.internal_path_length == 25

    # Test BST internal structure
    def test_delete_root(self, t, expect_set):
        # delete the root (default deletion)
        assert t._root.key == 'S'
        del t['S']
        assert len(t) == len(expect_set) - 1
        assert t._root.key == 'X'
        assert t._root.left.key == 'E'
        assert t._root.right is None

    def test_hibbard_delete(self, ST, data):
        t = ST(data, delete_method='Hibbard')
        assert t._root.key == 'S'
        del t['S']
        assert t._root.key == 'X'
        assert t._root.left.key == 'E'
        assert t._root.right is None

    def test_predecessor_delete(self, ST, data):
        t = ST(data, delete_method='Hibbard_p')
        assert t._root.key == 'S'
        del t['S']
        assert t._root.key == 'R'
        assert t._root.left.key == 'E'
        assert t._root.right.key == 'X'


# -----------------------------------------------------------------------------
#         Test ThreadedST methods
# -----------------------------------------------------------------------------
@pytest.mark.parametrize('ST', [ThreadedST, ThreadedST_nr])
class TestThreadedSTs:
    @staticmethod
    def run_threads(t, expect_set):
        """Test that the next/prev attributes are set properly."""
        keys = sorted(expect_set)
        for i, k in enumerate(keys[:-1]):
            assert t.next(k) == keys[i+1]
        assert t.next(keys[-1]) is None

        keys = sorted(expect_set, reverse=True)
        for i, k in enumerate(keys[:-1]):
            assert t.prev(k) == keys[i+1]
        assert t.prev(keys[-1]) is None

    def test_threads(self, t, expect_set):
        self.run_threads(t, expect_set)

    def test_delete_min(self, t, expect_set):
        k, v = t.min(), t[t.min()]
        t.delete_min()  # remove 'A'
        self.run_threads(t, sorted(expect_set - set(k)))
        t[k] = v

    def test_delete_max(self, t, expect_set):
        k, v = t.max(), t[t.max()]
        t.delete_max()  # remove 'X'
        self.run_threads(t, sorted(expect_set - set(k)))
        t[k] = v

    def test_delete(self, ST, data, expect_set):
        # Delete arbitrary key, starting with same tree
        for k in expect_set:
            t = ST(data)
            del t[k]
            self.run_threads(t, sorted(expect_set - set(k)))

# =============================================================================
# =============================================================================
