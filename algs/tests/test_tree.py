#!/usr/bin/env python3
# =============================================================================
#     File: test_tree.py
#  Created: 2021-04-15 14:00
#   Author: Bernie Roesler
#
"""
Tests specific to BST data types, not including balanced trees.
"""
# =============================================================================

import pytest

from algs.search.tree import BST, BST_nr, ThreadedST, ThreadedST_nr
from algs.tests.test_search import items, st, expect_set

TREES = set([BST, BST_nr, ThreadedST, ThreadedST_nr])

# -----------------------------------------------------------------------------
#         Test BST structure
# -----------------------------------------------------------------------------
@pytest.mark.parametrize('ST', TREES)
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

    def test_construction(self, st):
        assert st.isBST()
        # TODO test for each failure mode

    def test_orders(self, st):
        assert st.pre_order() ==   list('SEACRHMLPX')
        assert st.in_order() ==    list('ACEHLMPRSX')
        assert st.post_order() ==  list('CALPMHREXS')
        assert st.level_order() == list('SEXARCHMLP')

    def test_height(self, st, heights):
        assert st.height_r() == 5
        assert st.height == 5
        # Test height of each node individually
        t_heights = st.level_order(op=lambda x: (x.key, x.height))
        assert t_heights == heights
        del st['H']  # remove node with single child
        assert st.height_r() == 4
        assert st.height == 4

    def test_ipl_delete(self, st):
        assert st.internal_path_length_r() == 26
        assert st.internal_path_length == 26
        del st['H']  # remove node with single child
        assert st.internal_path_length == 20

    def test_ipl_insert(self, st):
        st['G'] = 6
        assert st.internal_path_length_r() == 30
        assert st.internal_path_length == 30
        del st['H']  # remove node with two children
        assert st.internal_path_length_r() == 25
        assert st.internal_path_length == 25

    # Test BST internal structure
    def test_delete_root(self, st, expect_set):
        # delete the root (default deletion)
        assert st._root.key == 'S'
        del st['S']
        assert len(st) == len(expect_set) - 1
        assert st._root.key == 'X'
        assert st._root.left.key == 'E'
        assert st._root.right is None

    def test_hibbard_delete(self, ST, items):
        st = ST(items, delete_method='Hibbard')
        assert st._root.key == 'S'
        del st['S']
        assert st._root.key == 'X'
        assert st._root.left.key == 'E'
        assert st._root.right is None

    def test_predecessor_delete(self, ST, items):
        st = ST(items, delete_method='Hibbard_p')
        assert st._root.key == 'S'
        del st['S']
        assert st._root.key == 'R'
        assert st._root.left.key == 'E'
        assert st._root.right.key == 'X'


# -----------------------------------------------------------------------------
#         Test ThreadedST methods
# -----------------------------------------------------------------------------
@pytest.mark.parametrize('ST', [ThreadedST, ThreadedST_nr])
class TestThreadedSTs:
    @staticmethod
    def run_threads(st, expect_set):
        """Test that the next/prev attributes are set properly."""
        keys = sorted(expect_set)
        for i, k in enumerate(keys[:-1]):
            assert st.next(k) == keys[i+1]
        assert st.next(keys[-1]) is None

        keys = sorted(expect_set, reverse=True)
        for i, k in enumerate(keys[:-1]):
            assert st.prev(k) == keys[i+1]
        assert st.prev(keys[-1]) is None

    def test_threads(self, st, expect_set):
        self.run_threads(st, expect_set)

    def test_delete_min(self, st, expect_set):
        k, v = st.min(), st[st.min()]
        st.delete_min()  # remove 'A'
        self.run_threads(st, sorted(expect_set - set(k)))
        st[k] = v

    def test_delete_max(self, st, expect_set):
        k, v = st.max(), st[st.max()]
        st.delete_max()  # remove 'X'
        self.run_threads(st, sorted(expect_set - set(k)))
        st[k] = v

    def test_delete(self, ST, items, expect_set):
        # Delete arbitrary key, starting with same tree
        for k in expect_set:
            st = ST(items)
            del st[k]
            self.run_threads(st, sorted(expect_set - set(k)))

# =============================================================================
# =============================================================================
