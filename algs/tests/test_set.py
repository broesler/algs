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

from algs.tests.test_search import err_test, expect_ranks
from algs.search.set import (Set, HashSet,
                             MultiHashSet, MultiSet,
                             MultiKeyHashSet, MultiKeySet,
                             MathSet, MathMultiSet)

# TODO
#   * implement Set and HashSet using built-in `set`?
#   * deprecate `delete` -> `remove`.

# Determine which classes to test
UNORDERED_SETS = set([HashSet, MultiHashSet, MultiKeyHashSet])
ORDERED_SETS = set([Set, MultiSet, MultiKeySet])
MATH_SETS = set([MathSet, MathMultiSet])

MULTISETS = set([MultiHashSet, MultiSet, MultiKeyHashSet, MultiKeySet])
MATH_MULTISETS = set([MathMultiSet])

ALL_SETS = UNORDERED_SETS | ORDERED_SETS | MATH_SETS

# Define fixtures common to each test
EXPECT_STR = 'SEARCHEXAMPLE'


@pytest.fixture
def expect_set(SET):
    if 'Multi' in SET.__name__:
        return list(EXPECT_STR)
    else:
        return set(EXPECT_STR)


@pytest.fixture
def keys():
    return list(EXPECT_STR)


@pytest.fixture
def U_keys():
    """The universe of all possible keys."""
    return string.ascii_uppercase


@pytest.fixture
def empty_set(SET, U_keys):
    if SET in MATH_SETS:
        return SET(U_keys)
    else:
        return SET()


@pytest.fixture
def st(SET, U_keys, keys):
    if SET in MATH_SETS:
        return SET(U_keys, keys)
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
        err_test(empty_set, '__delitem__', 'Z', err_type=KeyError)

    def test_add_single(self, empty_set):
        t = empty_set
        t.add('A')
        assert 'A' in t

    def test_contains(self, st, keys, expect_set):
        for k in keys:
            assert k in st
        assert 'B' not in st

    def test_size(self, st, expect_set):
        assert len(st) == len(expect_set)
        assert len(st) == st.size()

    def test_equality(self, st, expect_set):
        assert st == expect_set

    def test_iteration(self, st, expect_set):
        for k in st:
            assert k in expect_set
        assert sorted(st) == sorted(expect_set)

    def test_delete_all(self, st, keys, expect_set):
        test_keys = expect_set.copy()
        N_expect = len(expect_set)
        for k in set(expect_set):  # multi removes all
            del st[k]
            assert k not in st
            i = 0
            while k in test_keys:
                test_keys.remove(k)
                i += 1  # count multiplicity for multisets
            N_expect -= i
            assert st.size() == N_expect
            assert sorted(st) == sorted(test_keys)
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

    def test_select_raises(self, st):
        err_test(st, 'select', -1, err_type=IndexError)  # too small
        err_test(st, 'select', 99, err_type=IndexError)  # too large

    def test_delete_min(self, st, expect_set):
        assert st.min() == 'A'
        st.delete_min()  # remove 'A'
        assert st.min() == 'C'

    def test_delete_max(self, st, expect_set):
        assert st.max() == 'X'
        st.delete_max()  # remove 'X'
        assert st.max() == 'S'

    def test_range(self, st, expect_set):
        assert st == sorted(expect_set)
        assert st.keys(lo='P') == list('PRSX')
        assert st.size(lo='P') == 4
        assert st.keys('F', 'P') == list('HLMP')
        assert st.size('F', 'P') == 4
        if 'Multi' in st.__class__.__name__:
            assert st.keys(hi='P') == list('AACEEEHLMP')
            assert st.size(hi='P') == 10
        else:
            assert st.keys(hi='P') == list('ACEHLMP')
            assert st.size(hi='P') == 7

    # TODO fix *tests* for multi (and possibly MultiKeySet)
    # Rank for each key should be minimum index.
    # Select should return same key for multiple indices.
    def test_rank(self, st, expect_ranks, expect_set):
        for i, c in zip(expect_ranks, sorted(expect_set)):
            assert st.rank(c) == i

    def test_select(self, st, expect_set):
        for i, c in enumerate(sorted(expect_set)):
            assert st.select(i) == c

    def test_rankselect(self, st, expect_ranks, expect_set):
        # Ex 3.2.33
        for k in st:
            assert st.select(st.rank(k)) == k
        # TODO fails for multi since rank is lowest value for given key.
        for i, c in zip(expect_ranks, sorted(expect_set)):
            assert st.rank(st.select(i)) == i


# -----------------------------------------------------------------------------
#         Mathematical sets
# -----------------------------------------------------------------------------
@pytest.fixture
def U(SET, U_keys):
    return SET(U_keys, U_keys)


@pytest.fixture
def A(SET, U):
    return SET(U, 'ABCDE')


@pytest.fixture
def B(SET, U):
    return SET(U, 'DEF')


@pytest.mark.parametrize('SET', MATH_SETS)
class TestMathSet:
    def test_empty_set(self, empty_set, A, U):
        assert empty_set.complement() == U
        assert A | empty_set == A
        assert A & empty_set == empty_set
        assert A - empty_set == A
        assert A ^ empty_set == A

    def test_complement(self, SET, A, U):
        assert A.complement() == SET(U, 'FGHIJKLMNOPQRSTUVWXYZ')

    def test_universe(self, A, U):
        assert U.is_superset(A)
        assert A.is_subset(U)

    def test_ops(self, SET, A, B, U):
        assert A.union(B) == SET(U, 'ABCDEF')
        assert A.intersection(B) == SET(U, 'DE')
        assert A.difference(B) == SET(U, 'ABC')
        assert A.xor(B) == SET(U, 'ABCF')

    def test_shorthand(self, SET, A, B, U):
        assert A | B == SET(U, 'ABCDEF')
        assert A & B == SET(U, 'DE')
        assert A - B == SET(U, 'ABC')
        assert A ^ B == SET(U, 'ABCF')

    def test_ior(self, SET, A, B, U):
        A |= B
        assert A == SET(U, 'ABCDEF')

    def test_iand(self, SET, A, B, U):
        A &= B
        assert A == SET(U, 'DE')

    def test_isub(self, SET, A, B, U):
        A -= B
        assert A == SET(U, 'ABC')

    def test_ixor(self, SET, A, B, U):
        A ^= B
        assert A == SET(U, 'ABCF')

    def test_subsuper(self, A, B, U):
        assert U.is_superset(A)
        assert A.is_subset(U)
        assert not A.is_superset(B)
        assert not A.is_subset(B)

    def test_compare(self, A, U):
        # Identity operations
        assert A == A
        assert A >= A
        assert A <= A
        # Comparison with universe
        assert U > A
        assert A < U
        assert U >= A
        assert A <= U
        assert A != U


# -----------------------------------------------------------------------------
#         Multisets
# -----------------------------------------------------------------------------
@pytest.fixture
def Am(SET, U):
    return SET(U, 'AAB')


@pytest.fixture
def Bm(SET, U):
    return SET(U, 'BBC')


@pytest.fixture
def Cm(SET, U):
    return SET(U, 'AAABBCC')


@pytest.mark.parametrize('SET', MATH_MULTISETS)
class TestMultiSets:
    def test_ops(self, SET, Am, Bm, U):
        assert Am.union(Bm) == SET(U, 'AABBC')
        assert Am.intersection(Bm) == SET(U, 'B')
        assert Am.difference(Bm) == SET(U, 'AA')
        assert Am.xor(Bm) == SET(U, 'AABC')
        assert Am.sum(Bm) == SET(U, 'AABBBC')

    def test_shorthand(self, SET, Am, Bm, U):
        assert Am | Bm == SET(U, 'AABBC')
        assert Am & Bm == SET(U, 'B')
        assert Am - Bm == SET(U, 'AA')
        assert Am ^ Bm == SET(U, 'AABC')
        assert Am + Bm == SET(U, 'AABBBC')

    def test_ior(self, SET, Am, Bm, U):
        Am |= Bm
        assert Am == SET(U, 'AABBC')

    def test_iand(self, SET, Am, Bm, U):
        Am &= Bm
        assert Am == SET(U, 'B')

    def test_isub(self, SET, Am, Bm, U):
        Am -= Bm
        assert Am == SET(U, 'AA')

    def test_ixor(self, SET, Am, Bm, U):
        Am ^= Bm
        assert Am == SET(U, 'AABC')

    def test_iadd(self, SET, Am, Bm, U):
        Am += Bm
        assert Am == SET(U, 'AABBBC')

    def test_subsuper(self, SET, Am, Bm, Cm, U):
        assert Cm.is_superset(Am)
        assert Am.is_subset(Cm)
        assert not Am.is_subset(SET(U, 'ABC'))
        assert not Am.is_superset(SET(U, 'AAA'))

    def test_compare(self, Am, Cm):
        # Identity operations
        assert Am == Am
        assert Am >= Am
        assert Am <= Am
        # Comparison with superset
        assert Cm > Am
        assert Am < Cm
        assert Cm >= Am
        assert Am <= Cm
        assert Am != Cm


# =============================================================================
# =============================================================================
