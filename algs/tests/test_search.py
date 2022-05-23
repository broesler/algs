#!/usr/bin/env python3
# =============================================================================
#     File: test_search.py
#  Created: 2021-03-02 09:18
#   Author: Bernie Roesler
#
"""
  Description: Unit tests for algs.search. Exercise 3.1.29 (and then some!)
"""
# =============================================================================

import numpy as np
import pytest

from algs.search import (SequentialSearchST, BinarySearchST, ArrayST, BST,
                         BST_nr, ThreadedST, ThreadedST_nr, ArrayBST,
                         RedBlackBST, TopDown234, TopDown234_nr,
                         TopDown234bothways, BottomUp234, Unbalanced23,
                         AVLTree,
                         SeparateChainingHashST, SeparateChainingLiteHashST,
                         LinearProbingHashST,
                         DoubleProbingHashST, DoubleHashingHashST)

rng = np.random.default_rng(seed=565656)


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


# Define fixtures common to each test
EXPECT_STR = 'SEARCHEXAMPLE'


@pytest.fixture
def expect_set():
    return set(EXPECT_STR)


@pytest.fixture
def data():
    return list((c, i) for i, c in enumerate(EXPECT_STR))


@pytest.fixture
def data_set(data):
    data_set = data.copy()
    data_set.remove(('E', 1))
    data_set.remove(('A', 2))
    data_set.remove(('E', 6))
    return data_set


# ---------- Test All STs ----------
UNORDERED_STS = set([SequentialSearchST, ArrayST,
                     SeparateChainingHashST, SeparateChainingLiteHashST,
                     LinearProbingHashST, 
                     DoubleProbingHashST, DoubleHashingHashST])
ORDERED_STS = set([BinarySearchST, BST, BST_nr, ThreadedST, ThreadedST_nr,
                   ArrayBST])
BALANCED_TREES = set([RedBlackBST, TopDown234, TopDown234_nr, BottomUp234,
                      TopDown234bothways, Unbalanced23, AVLTree])
ALL_STS = UNORDERED_STS | ORDERED_STS | BALANCED_TREES

NO_CACHE = set([ArrayBST,
                SeparateChainingHashST,
                SeparateChainingLiteHashST,
                LinearProbingHashST,
                DoubleProbingHashST,
                DoubleHashingHashST])


class TestUnorderedOps:
    @pytest.mark.parametrize('ST', ALL_STS)
    def test_empty_table(self, ST):
        st = ST(cache=False)
        assert st.size == 0
        assert st.is_empty
        assert st.keys() == []
        assert st.values() == []
        assert st.items() == []

    @pytest.mark.parametrize('ST', ALL_STS)
    def test_put_get(self, ST, data, expect_set, data_set):
        st = ST(data, cache=False)
        for k, v in data:
            assert k in st
            if k == 'E' or k == 'A':
                assert st[k] == max([val for key, val in data if key == k])
            else:
                assert st[k] == v
        assert len(st) == len(expect_set)
        assert len(st) == st.size
        # st.keys() not guaranteed in order, so these tests are weak
        assert sorted(st.keys()) == sorted(expect_set)
        assert sorted(st.values()) == sorted([v for k, v in data_set])
        assert sorted(st.items()) == sorted(data_set)
        err_test(st, '__getitem__', 'Z', err_type=KeyError)

    @pytest.mark.parametrize('ST', ALL_STS - set([ArrayBST, Unbalanced23,
                                                  DoubleProbingHashST,
                                                  DoubleHashingHashST]))
    def test_delete(self, ST, data, expect_set):
        st = ST(data, cache=False)
        test_keys = expect_set.copy()
        N_expect = len(expect_set)
        for k in list(st.keys()):
            del st[k]
            N_expect -= 1
            test_keys -= set(k)
            assert st.size == N_expect
            assert sorted(st.keys()) == sorted(test_keys)
        err_test(st, '__delitem__', 'Z', err_type=KeyError)
        assert st.is_empty

    @pytest.mark.parametrize('ST', ALL_STS - NO_CACHE)
    def test_cache_existing(self, ST, data):
        st = ST(data, cache=True)
        for k in st:
            v = st[k]   # __getitem__
            assert st._cache.key == k
            assert st._cache.val == v
            st[k] = 56  # __setitem__
            assert st._cache.key == k
            assert st._cache.val == 56
        del st[k]
        assert st._cache is None

    @pytest.mark.parametrize('ST', ALL_STS - NO_CACHE)
    def test_cache_new(self, ST, data):
        st = ST(cache=True)
        for k, v in data:
            st[k] = v  # __setitem__
            assert st._cache.key == k
            assert st._cache.val == v


class TestSelfOrg:
    def test_selforg_nocache(self, data):
        """Test self-organizing search (Exercise 3.1.22)"""
        st = ArrayST(data, selforg=True, cache=False)
        rand_keys = rng.choice(st.keys(), size=st.size)
        for k in rand_keys:
            st[k]                       # search for the key
            assert st.keys()[0] == k
            st[k]                       # search again
            assert st._cost == 1

    def test_selforg_cache(self, data):
        """Test self-organizing search AND caching."""
        st = ArrayST(data, selforg=True, cache=True)
        rand_keys = rng.choice(st.keys(), size=st.size)
        for k in rand_keys:
            st[k]                       # search for the key
            assert st.keys()[0] == k
            assert st._cache.key == k
        del st[k]
        assert st._cache is None


# ---------- Test Ordered Operations ----------
@pytest.fixture
def empty_t(ST, cache):
    return ST(cache=cache)


@pytest.fixture
def t(ST, cache, data):
    return ST(data, cache=cache)


def test_binary_integrity(data):
    t = BinarySearchST(data)
    assert t._assert_integrity() is None


@pytest.mark.parametrize('ST', ORDERED_STS - set([ArrayBST]))
@pytest.mark.parametrize('cache', [False, True])
class TestOrderedOps:
    def test_bad_input(self, empty_t):
        err_test(empty_t, '__init__', list('BADEXAMPLE'), err_type=ValueError)

    def test_empty_table(self, empty_t):
        assert empty_t.size == 0
        assert empty_t.is_empty
        assert empty_t.keys() == []
        assert empty_t.values() == []
        assert empty_t.items() == []
        assert empty_t.floor('A') is None
        assert empty_t.ceil('A') is None
        assert empty_t.rank('A') == 0

    def test_empty_raises(self, empty_t):
        err_test(empty_t, '__getitem__', 'A', err_type=KeyError)
        err_test(empty_t, 'min', err_type=KeyError)
        err_test(empty_t, 'max', err_type=KeyError)
        err_test(empty_t, 'delete_min', err_type=KeyError)
        err_test(empty_t, 'delete_max', err_type=KeyError)
        err_test(empty_t, 'select', 0, err_type=IndexError)

    def test_put_get(self, empty_t):
        # Test insert/get single node
        t = empty_t
        t['A'] = 0
        assert t['A'] == 0

    def test_len(self, t, expect_set):
        assert len(t) == len(expect_set)
        assert len(t) == t.size

    def test_contains(self, t, data):
        for k, v in data:
            # test __contains__
            assert k in t

            # test __getitem__
            if k == 'E' or k == 'A':
                assert t[k] == max([v for key, v in data if key == k])
            else:
                assert t[k] == v

        # Test __contains__ for item *not* in table
        assert 'B' not in t

    def test_minmax(self, t):
        assert t.min() == 'A'
        assert t.max() == 'X'

    def test_floorceil(self, t):
        assert t.floor('H') == 'H'
        assert t.ceil('H')  == 'H'
        assert t.floor('Q') == 'P'
        assert t.ceil('Q')  == 'R'
        assert t.floor(chr(ord('A') - 1)) is None  # char < t.min(
        assert t.ceil('Z') is None                 # char > t.max(

    def test_rankselect(self, t, expect_set):
        # Select and Rank tests
        err_test(t, 'select', -1, err_type=IndexError)  # too small
        for i, c in enumerate(sorted(expect_set)):
            assert t.select(i) == c
            assert t.rank(c) == i
        err_test(t, 'select', 99, err_type=IndexError)  # too large

        # Ex 3.2.33
        for i in range(t.size):
            assert t.rank(t.select(i)) == i

        for k in t.keys():
            assert t.select(t.rank(k)) == k

    def test_inorder(self, t, data_set, expect_set):
        # In-order traversal + range search
        assert list(t.keys()) == sorted(expect_set)
        assert list(t.keys(lo='P')) == list('PRSX')
        assert list(t.keys('F', 'P')) == list('HLMP')
        assert list(t.keys(hi='P')) == list('ACEHLMP')
        assert list(t.values()) == [v for k, v in sorted(data_set)]
        assert (list(t.values('F', 'P')) ==
                [v for k, v in sorted(data_set)[3:7]])
        assert list(t.items()) == sorted(data_set)
        assert list(t.items('F', 'P')) == sorted(data_set)[3:7]

    def test_delete_min(self, t, expect_set):
        # Test deletion and reinsertion
        k, v = t.min(), t[t.min()]
        t.delete_min()  # remove 'A'
        assert t.min() == 'C'
        # Test updated ranks
        for i, c in enumerate(sorted(expect_set - set(k))):
            assert t.select(i) == c
            assert t.rank(c) == i
        t[k] = v  # replace value

    def test_delete_max(self, t, expect_set):
        k, v = t.max(), t[t.max()]
        t.delete_max()  # remove 'X'
        assert t.max() == 'S'
        # Test updated ranks
        for i, c in enumerate(sorted(expect_set - set(k))):
            assert t.select(i) == c
            assert t.rank(c) == i
        t[k] = v  # replace value

    def test_delete(self, ST, data, cache, expect_set):
        # Delete arbitrary key, starting with same tree
        for k in expect_set:
            t = ST(data, cache=cache)
            t[k]  # get item
            del t[k]
            assert len(t) == len(expect_set)-1
            err_test(t, '__getitem__', k, err_type=KeyError)


def test_comparisons(data):
    assert SequentialSearchST(data) == BinarySearchST(data)
    assert BinarySearchST(data) == SequentialSearchST(data)
    assert BinarySearchST(data) == BST(data)
    assert BST(data) == BinarySearchST(data)
    assert BST(data) == BST_nr(data)
    assert BST_nr(data) == BST(data)


# =============================================================================
# =============================================================================
