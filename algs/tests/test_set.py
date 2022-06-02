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

from algs.search.set import Set, HashSet


def err_test(container, op, *args, err_type=IndexError):
    """Test for raising a given error type.

    Parameters
    ----------
    container : list-like container data type instance
        A class instance to be tested.
    op : str
        attribute name of method to test
    *args : list
        arguments to `op`.
    err_type : Exception, optional
        error type that object is expected to raise

    Raises
    ------
    Exception
        If error raised is not of type `err_type`.
    """
    with pytest.raises(err_type):
        getattr(container, op)(*args)  # call the method


# Determine which classes to test
UNORDERED_SETS = set([HashSet])
ORDERED_SETS = set([Set])
ALL_SETS = UNORDERED_SETS | ORDERED_SETS

# Define fixtures common to each test
EXPECT_STR = 'SEARCHEXAMPLE'


@pytest.fixture
def expect_set():
    return set(EXPECT_STR)


@pytest.fixture
def data():
    return list(EXPECT_STR)


@pytest.fixture
def empty_set(SET):
    return SET()


@pytest.fixture
def st(SET, data):
    return SET(data)


# -----------------------------------------------------------------------------
#         Run Tests
# -----------------------------------------------------------------------------
def test_comparisons(data):
    assert Set(data) == HashSet(data)


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

    def test_contains(self, st, data, expect_set):
        for k in data:
            assert k in st
        assert len(st) == len(expect_set)
        assert len(st) == st.size()
        assert st == expect_set
        assert 'B' not in st

    def test_iteration(self, st, expect_set):
        for k in st:
            assert k in expect_set

    def test_delete(self, st, data, expect_set):
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


# ---------- Test Ordered Operations ----------
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
        assert st.keys('F', 'P') == list('HLMP')
        assert st.keys(hi='P') == list('ACEHLMP')

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


# =============================================================================
# =============================================================================
