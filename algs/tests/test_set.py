#!/usr/bin/env python3
# =============================================================================
#     File: test_set.py
#  Created: 2022-05-31 19:07
#   Author: Bernie Roesler
#
"""
Unit tests for Sets. Similar to tests for `algs.search` without values.
"""
# =============================================================================

import pytest
import string

from algs.tests.test_search import err_test
from algs.search.set import invert, Set, HashSet, MathSet


# Determine which classes to test
UNORDERED_SETS = set([HashSet])
ORDERED_SETS = set([Set])
MATH_SETS = set([MathSet])
ALL_SETS = UNORDERED_SETS | ORDERED_SETS | MATH_SETS

# Define fixtures common to each test
EXPECT_STR = 'SEARCHEXAMPLE'


@pytest.fixture
def expect_set():
    return set(EXPECT_STR)


@pytest.fixture
def keys():
    return list(EXPECT_STR)


@pytest.fixture
def U():
    """The universe of all possible keys."""
    return string.ascii_uppercase


@pytest.fixture
def empty_set(SET, U):
    if SET in MATH_SETS:
        return SET(U)
    else:
        return SET()


@pytest.fixture
def st(SET, U, keys):
    if SET in MATH_SETS:
        return SET(U, keys)
    else:
        return SET(keys)


# -----------------------------------------------------------------------------
#         Run Tests
# -----------------------------------------------------------------------------
def test_comparisons(keys):
    assert Set(keys) == HashSet(keys)


@pytest.mark.parametrize('SET', ALL_SETS)
class TestUnorderedOps:
    def test_empty_set(self, empty_set):
        assert empty_set.size() == 0
        assert empty_set.is_empty
        assert len(empty_set) == 0

    def test_empty_raises(self, empty_set):
        err_test(empty_set, '__setitem__', 'A', 1,  err_type=AttributeError)
        err_test(empty_set, '__getitem__', 'A', err_type=AttributeError)

    def test_add_single(self, empty_set):
        t = empty_set
        t.add('A')
        assert 'A' in t

    def test_contains(self, st, keys, expect_set):
        for k in keys:
            assert k in st
        assert len(st) == len(expect_set)
        assert len(st) == st.size()
        assert st == expect_set
        assert 'B' not in st

    def test_iteration(self, st, expect_set):
        for k in st:
            assert k in expect_set
        assert sorted(st) == sorted(expect_set)

    def test_delete(self, st, keys, expect_set):
        test_keys = expect_set.copy()
        N_expect = len(expect_set)
        for k in st:
            del st[k]
            N_expect -= 1
            test_keys -= set(k)
            assert st.size() == N_expect
            assert sorted(st) == sorted(test_keys)
        err_test(st, '__delitem__', 'Z', err_type=KeyError)
        assert st.is_empty


@pytest.mark.parametrize('SET', ORDERED_SETS)
class TestOrderedOps:
    def test_empty_set(self, empty_set):
        assert empty_set.floor('A') is None
        assert empty_set.ceil('A') is None
        assert empty_set.rank('A') == 0

    def test_empty_raises(self, empty_set):
        err_test(empty_set, 'min', err_type=KeyError)
        err_test(empty_set, 'max', err_type=KeyError)
        err_test(empty_set, 'delete_min', err_type=KeyError)
        err_test(empty_set, 'delete_max', err_type=KeyError)
        err_test(empty_set, 'select', 0, err_type=IndexError)

    def test_minmax(self, st):
        assert st.min() == 'A'
        assert st.max() == 'X'

    def test_floorceil(self, st):
        assert st.floor('H') == 'H'
        assert st.ceil('H') == 'H'
        assert st.floor('Q') == 'P'
        assert st.ceil('Q') == 'R'
        assert st.floor(chr(ord('A') - 1)) is None  # char < st.min()
        assert st.ceil('Z') is None                 # char > st.max()

    def test_rankselect(self, st, expect_set):
        # Select and Rank tests
        err_test(st, 'select', -1, err_type=IndexError)  # too small
        for i, c in enumerate(sorted(expect_set)):
            assert st.select(i) == c
            assert st.rank(c) == i
        err_test(st, 'select', 99, err_type=IndexError)  # too large

        # Ex 3.2.33
        for i in range(st.size()):
            assert st.rank(st.select(i)) == i

        for k in st:
            assert st.select(st.rank(k)) == k

    def test_range(self, st, expect_set):
        assert st == sorted(expect_set)
        assert st.keys(lo='P') == list('PRSX')
        assert st.size(lo='P') == 4
        assert st.keys('F', 'P') == list('HLMP')
        assert st.size('F', 'P') == 4
        assert st.keys(hi='P') == list('ACEHLMP')
        assert st.size(hi='P') == 7

    def test_delete_min(self, st, expect_set):
        # Test deletion and reinsertion
        k = st.min()
        st.delete_min()  # remove 'A'
        assert st.min() == 'C'
        # Test updated ranks
        for i, c in enumerate(sorted(expect_set - set(k))):
            assert st.select(i) == c
            assert st.rank(c) == i

    def test_delete_max(self, st, expect_set):
        k = st.max()
        st.delete_max()  # remove 'X'
        assert st.max() == 'S'
        # Test updated ranks
        for i, c in enumerate(sorted(expect_set - set(k))):
            assert st.select(i) == c
            assert st.rank(c) == i


# -----------------------------------------------------------------------------
#         Mathematical sets
# -----------------------------------------------------------------------------
@pytest.fixture
def A_keys():
    return 'ABCDE'


@pytest.fixture
def A(SET, U, A_keys):
    return SET(U, A_keys)


@pytest.fixture
def B(SET, U):
    return SET(U, 'DEF')

@pytest.fixture
def C(SET, U):
    return SET(U, 'ABC')


@pytest.fixture
def D(SET, U):
    return SET(U, 'ABCDEFGH')


@pytest.fixture
def U_set(SET, U):
    return SET(U, U)


@pytest.mark.parametrize('SET', MATH_SETS)
class TestMathSet:
    def test_empty_set(self, empty_set, A, U_set):
        assert empty_set.complement() == U_set
        assert A | empty_set == A
        assert A & empty_set == empty_set
        assert A - empty_set == A
        assert A ^ empty_set == A

    def test_complement(self, A, U, A_keys):
        assert A.complement() == MathSet(U, 'FGHIJKLMNOPQRSTUVWXYZ')

    def test_universe(self, A, U_set):
        assert U_set.is_superset(A)
        assert A.is_subset(U_set)

    def test_ops(self, A, B, U):
        assert A | B == MathSet(U, 'ABCDEF')
        assert A & B == MathSet(U, 'DE')
        assert A - B == MathSet(U, 'ABC')
        assert A ^ B == MathSet(U, 'ABCF')

    def test_subsuper(self, A, B, C, D):
        assert not A.is_superset(B)
        assert not A.is_subset(B)
        assert A.is_superset(C)
        assert C.is_subset(A)
        assert A.is_subset(D)
        assert B.is_subset(D)
        assert C.is_subset(D)
        assert D.is_superset(A)

# =============================================================================
# =============================================================================
