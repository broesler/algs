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


class TestRotations:
    # TODO try rewriting these as parameters instead of fixtures
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
        hs = [0, 0]
        ipls = [0, 0]
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
        # hs = [3, 2, 2, 1, 1, 0, 1, 0, 0, 0]  # no red adjust
        hs = [2, 1, 1, 0, 0, 0, 0, 0, 0, 0]
        ipls = []  # dummy list for now
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


# Interactive test setup
if __name__ == '__main__':
    EXPECT_STR = 'SEARCHEXAMPLE'
    data = list((c, i) for i, c in enumerate(EXPECT_STR))
    st = RedBlackBST(data)
    # FIXME root is not black? or printing does not work at root

# =============================================================================
# =============================================================================
