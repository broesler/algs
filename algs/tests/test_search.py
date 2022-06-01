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
                         LinearProbingHashST, LazyLinearProbingHashST,
                         DoubleProbingHashST, DoubleHashingHashST,
                         CuckooHashST)

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


# ---------- Test All STs ----------
UNORDERED_STS = set([SequentialSearchST, ArrayST,
                     SeparateChainingHashST, SeparateChainingLiteHashST,
                     LinearProbingHashST, LazyLinearProbingHashST,
                     DoubleProbingHashST, DoubleHashingHashST,
                     CuckooHashST])

ORDERED_STS = set([BinarySearchST, BST, BST_nr, ThreadedST, ThreadedST_nr,
                   ArrayBST])

BALANCED_TREES = set([RedBlackBST, TopDown234, TopDown234_nr, BottomUp234,
                      TopDown234bothways, Unbalanced23, AVLTree])

ALL_STS = UNORDERED_STS | ORDERED_STS | BALANCED_TREES

NO_DELETE = set([ArrayBST,
                 Unbalanced23,
                 ])

NO_CACHE = set([ArrayBST,
                SeparateChainingHashST,
                SeparateChainingLiteHashST,
                LinearProbingHashST,
                LazyLinearProbingHashST,
                DoubleProbingHashST,
                DoubleHashingHashST,
                CuckooHashST,
                ])


# -----------------------------------------------------------------------------
#         Define fixtures common to each test
# -----------------------------------------------------------------------------
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


@pytest.fixture
def empty_st(ST, cache):
    return ST(cache=cache)


@pytest.fixture
def st(ST, cache, data):
    return ST(data, cache=cache)


# -----------------------------------------------------------------------------
#         Run Tests
# -----------------------------------------------------------------------------
@pytest.mark.parametrize('cache', [False, True])
class TestUnorderedOps:
    @pytest.mark.parametrize('ST', ALL_STS)
    class TestPutGet:
        def test_bad_input(self, empty_st):
            err_test(empty_st, '__init__', list('BADEXAMPLE'),
                     err_type=ValueError)

        def test_empty_table(self, empty_st):
            assert empty_st.size == 0
            assert empty_st.is_empty
            assert empty_st.keys() == []
            assert empty_st.values() == []
            assert empty_st.items() == []

        def test_add_single(self, empty_st):
            # Test insert/get single node
            st = empty_st
            st['A'] = 0
            assert st['A'] == 0

        def test_alias(self, empty_st):
            st = empty_st
            st.put('A', 0)
            assert 'A' in st
            assert st.get('A') == 0

        def test_contains(self, st, expect_set):
            for k in expect_set:
                assert k in st
            assert 'B' not in st

        def test_iteration(self, st, expect_set):
            for k in st:
                assert k in expect_set

        def test_put_get(self, st, data, expect_set, data_set):
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

    @pytest.mark.parametrize('ST', ALL_STS - NO_DELETE)
    class TestDelete:
        def test_delete_one(self, ST, data, cache, expect_set):
            # Delete arbitrary key, starting with same table
            for k in expect_set:
                t = ST(data, cache=cache)
                t[k]    # get item to ensure cache is used
                del t[k]
                # assert len(t) == len(expect_set)-1
                assert k not in t
                assert sorted(t.keys()) == sorted(expect_set - set(k))
                err_test(t, '__getitem__', k, err_type=KeyError)

        def test_alias(self, empty_st):
            st = empty_st
            st.put('A', 0)
            st.delete('A')
            assert 'A' not in st
            assert st.is_empty

        def test_delete_all(self, st, data, expect_set):
            test_keys = expect_set.copy()
            N_expect = len(expect_set)
            for k in st:
                del st[k]
                N_expect -= 1
                test_keys -= set(k)
                assert st.size == N_expect
                assert sorted(st.keys()) == sorted(test_keys)
            err_test(st, '__delitem__', 'Z', err_type=KeyError)
            assert st.is_empty


@pytest.mark.parametrize('ST', ALL_STS - NO_CACHE)
@pytest.mark.parametrize('cache', [True])
class TestCaching:
    def test_cache_existing(self, st, data):
        for k in st:
            v = st[k]   # __getitem__
            assert st._cache.key == k
            assert st._cache.val == v
            st[k] = 56  # __setitem__
            assert st._cache.key == k
            assert st._cache.val == 56
        del st[k]
        assert st._cache is None

    def test_cache_new(self, st, data):
        for k, v in data:
            st[k] = v  # __setitem__
            assert st._cache.key == k
            assert st._cache.val == v


# Tests specific to a single data type
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
def test_binary_integrity(data):
    st = BinarySearchST(data)
    st._assert_integrity()


@pytest.mark.parametrize('ST', ORDERED_STS - set([ArrayBST]))
@pytest.mark.parametrize('cache', [False, True])
class TestOrderedOps:
    def test_empty_table(self, empty_st):
        assert empty_st.floor('A') is None
        assert empty_st.ceil('A') is None
        assert empty_st.rank('A') == 0

    def test_empty_raises(self, empty_st):
        err_test(empty_st, '__getitem__', 'A', err_type=KeyError)
        err_test(empty_st, 'min', err_type=KeyError)
        err_test(empty_st, 'max', err_type=KeyError)
        err_test(empty_st, 'delete_min', err_type=KeyError)
        err_test(empty_st, 'delete_max', err_type=KeyError)
        err_test(empty_st, 'select', 0, err_type=IndexError)

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
        for i in range(st.size):
            assert st.rank(st.select(i)) == i

        for k in st.keys():
            assert st.select(st.rank(k)) == k

    def test_inorder(self, st, data_set, expect_set):
        # In-order traversal + range search
        assert st.keys() == sorted(expect_set)
        assert st.keys(lo='P') == list('PRSX')
        assert st.keys('F', 'P') == list('HLMP')
        assert st.keys(hi='P') == list('ACEHLMP')
        assert st.values() == [v for k, v in sorted(data_set)]
        assert (st.values('F', 'P') ==
                [v for k, v in sorted(data_set)[3:7]])
        assert st.items() == sorted(data_set)
        assert st.items('F', 'P') == sorted(data_set)[3:7]

    def test_delete_min(self, st, expect_set):
        # Test deletion and reinsertion
        k, v = st.min(), st[st.min()]
        st.delete_min()  # remove 'A'
        assert st.min() == 'C'
        # Test updated ranks
        for i, c in enumerate(sorted(expect_set - set(k))):
            assert st.select(i) == c
            assert st.rank(c) == i
        st[k] = v  # replace value

    def test_delete_max(self, st, expect_set):
        k, v = st.max(), st[st.max()]
        st.delete_max()  # remove 'X'
        assert st.max() == 'S'
        # Test updated ranks
        for i, c in enumerate(sorted(expect_set - set(k))):
            assert st.select(i) == c
            assert st.rank(c) == i
        st[k] = v  # replace value


def test_comparisons(data):
    assert SequentialSearchST(data) == BinarySearchST(data)
    assert BinarySearchST(data) == SequentialSearchST(data)
    assert BinarySearchST(data) == BST(data)
    assert BST(data) == BinarySearchST(data)
    assert BST(data) == BST_nr(data)
    assert BST_nr(data) == BST(data)


# =============================================================================
# =============================================================================
