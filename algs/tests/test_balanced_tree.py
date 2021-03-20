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
from algs.tests.test_search import data


@pytest.fixture
def t(data):
    return RedBlackBST(data)


class TestRotations:
    # NOTE keys must be in special order, expected outputs are in *level* order
    @pytest.fixture
    def insert_no_rotate(self):
        keys = list('SAX')  # level-order = SAX
        Ns = [3, 1, 1]
        hs = [1, 0, 0]
        ipls = [2, 0, 0]
        return keys, Ns, hs, ipls

    @pytest.fixture
    def left_rotate(self):
        keys = list('ES')  # level-order = SE
        Ns = [2, 1]
        hs = [1, 0]
        # hs = [0, 0]  # red shift
        ipls = [1, 0]
        # ipls = [0, 0]  # red shift
        return keys, Ns, hs, ipls

    @pytest.fixture
    def right_rotate(self):
        keys = list('SEA')  # level-order = EAS
        Ns = [3, 1, 1]
        hs = [1, 0, 0]
        ipls = [2, 0, 0]
        return keys, Ns, hs, ipls

    @pytest.fixture
    def search_example(self):
        keys = list('SEARCHEXAMPLE')  # level-order = MERCLPXAHS
        Ns = [10, 5, 4, 2, 2, 1, 2, 1, 1, 1]
        hs = [3, 2, 2, 1, 1, 0, 1, 0, 0, 0]
        # hs = [2, 1, 1, 0, 0, 0, 0, 0, 0, 0]  # red shift
        ipls = [19, 6, 4, 1, 1, 0, 1, 0, 0, 0]
        # ipls = [10, 2, 2, 0, 0, 0, 0, 0, 0, 0]  # red shift
        return keys, Ns, hs, ipls

    @pytest.mark.parametrize('the_input',
                             ['insert_no_rotate',
                              'left_rotate',
                              'right_rotate',
                              'search_example'])
    def test_node_update(self, the_input, request):
        keys, Ns, hs, ipls = request.getfixturevalue(the_input)
        t = RedBlackBST.fromkeys(keys)
        assert t.level_order(op=lambda x: x.N) == Ns
        assert t.level_order(op=lambda x: x.height) == hs
        assert t.level_order(op=lambda x: x.ipl) == ipls


class TestCertification:
    def test_is23(self, t):
        assert t.is23()

    def test_isnot23a(self, t):
        t._root.left.left.color = t._RED  # t._root.left.left.left is also red
        assert not t.is23()

    def test_isnot23b(self, t):
        t._root.right.color = t._RED  # right-leaning red link
        assert not t.is23()

    def test_is_balanced(self, t):
        assert t.is_balanced()

    def test_is_not_balanced(self, t):
        t._root.left.left.left.color = t._BLACK
        assert not t.is_balanced()

    def test_isRedBlackBST(self, t):
        assert t.isRedBlackBST()

# =============================================================================
# =============================================================================
