#!/usr/bin/env python3
# =============================================================================
#     File: test_search.py
#  Created: 2021-03-02 09:18
#   Author: Bernie Roesler
# =============================================================================

"""Unit tests for algs.search. Exercise 3.1.29 (and then some!)."""

import numpy as np
import pytest

from algs.search import (
    BST,
    ArrayBST,
    ArrayST,
    AVLTree,
    BinarySearchST,
    BottomUp234,
    BST_nr,
    CuckooHashST,
    DoubleHashingHashST,
    DoubleProbingHashST,
    LazyLinearProbingHashST,
    LIFOHashST,
    LinearProbingHashST,
    MultiValBST,
    MultiValHashST,
    MultiValRedBlackBST,
    RedBlackBST,
    RobinHoodHashST,
    SeparateChainingHashST,
    SeparateChainingLiteHashST,
    SequentialSearchST,
    ThreadedST,
    ThreadedST_nr,
    TopDown234,
    TopDown234_nr,
    TopDown234bothways,
    Unbalanced23,
)
from algs.search.set import invert

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
UNORDERED_STS = {
    SequentialSearchST,
    ArrayST,
    SeparateChainingHashST,
    SeparateChainingLiteHashST,
    LinearProbingHashST,
    LazyLinearProbingHashST,
    DoubleProbingHashST,
    DoubleHashingHashST,
    CuckooHashST,
    LIFOHashST,
    RobinHoodHashST,
    MultiValHashST,
}

ORDERED_STS = {
    BinarySearchST,
    BST,
    BST_nr,
    ThreadedST,
    ThreadedST_nr,
    ArrayBST,
    RedBlackBST,
    TopDown234,
    TopDown234_nr,
    BottomUp234,
    TopDown234bothways,
    Unbalanced23,
    AVLTree,
    MultiValBST,
    MultiValRedBlackBST,
}

MULTIVAL_STS = {MultiValHashST, MultiValBST, MultiValRedBlackBST}

ALL_STS = UNORDERED_STS | ORDERED_STS

SINGLEVAL_STS = ALL_STS - MULTIVAL_STS

NO_DELETE = {
    ArrayBST,
    Unbalanced23,
    TopDown234bothways,
}

NO_CACHE = {
    ArrayBST,
    SeparateChainingHashST,
    SeparateChainingLiteHashST,
    LinearProbingHashST,
    LazyLinearProbingHashST,
    DoubleProbingHashST,
    DoubleHashingHashST,
    CuckooHashST,
    LIFOHashST,
    RobinHoodHashST,
}


# -----------------------------------------------------------------------------
#         Define fixtures common to each test
# -----------------------------------------------------------------------------
EXPECT_STR = 'SEARCHEXAMPLE'
ITEMS = tuple((c, i) for i, c in enumerate(EXPECT_STR))


@pytest.fixture
def expect_keys(ST):
    return set(EXPECT_STR)


@pytest.fixture
def expect_ranks(ST, expect_keys):
    return range(len(expect_keys))


@pytest.fixture
def expect_items():
    expect_items = list(ITEMS)
    expect_items.remove(('E', 1))
    expect_items.remove(('A', 2))
    expect_items.remove(('E', 6))
    return expect_items


@pytest.fixture
def empty_st(ST, cache):
    return ST(cache=cache)


@pytest.fixture
def st(ST, cache):
    return ST(ITEMS, cache=cache)


# TODO separate testing of keys from testing of values/items, then MultiVal*
# can be tested along with everything else, and only a few separate tests for
# multiple values.
# Multiple key testing (i.e. multisets) can occur in test_set instead.


# -----------------------------------------------------------------------------
#         Run Tests
# -----------------------------------------------------------------------------
@pytest.mark.parametrize('cache', [False, True])
class TestUnorderedOps:
    @pytest.mark.parametrize('ST', ALL_STS)
    class TestPut:
        def test_bad_input(self, empty_st):
            err_test(empty_st, '__init__', list('BADEXAMPLE'), err_type=ValueError)

        def test_empty_table(self, empty_st):
            assert empty_st.size() == 0
            assert empty_st.is_empty
            assert empty_st.keys() == []
            assert empty_st.values() == []
            assert empty_st.items() == []

        def test_empty_raises(self, empty_st):
            err_test(empty_st, '__getitem__', 'A', err_type=KeyError)

        def test_put_single(self, empty_st):
            # Test insert/get single key
            st = empty_st
            st['A'] = 0
            assert 'A' in st

        def test_alias(self, empty_st):
            st = empty_st
            st.put('A', 0)
            assert st.contains('A')

        def test_contains(self, st, expect_keys):
            for k in expect_keys:
                assert k in st
            assert 'B' not in st

        def test_put(self, st, expect_keys):
            for k in expect_keys:
                assert k in st

        def test_iteration(self, st, expect_keys):
            for k in st:
                assert k in expect_keys

        def test_keyerror(self, st):
            err_test(st, '__getitem__', 'Z', err_type=KeyError)

        def test_keys(self, st, expect_keys):
            # st.keys() not guaranteed in order, so these tests are weak
            assert sorted(st.keys()) == sorted(expect_keys)

    @pytest.mark.parametrize('ST', SINGLEVAL_STS)
    class TestGet:
        def test_alias(self, empty_st):
            st = empty_st
            st.put('A', 0)
            assert st.get('A') == 0

        def test_get(self, st, expect_keys):
            for k, v in ITEMS:
                if k in {'E', 'A'}:
                    assert st[k] == max([val for key, val in ITEMS if key == k])
                else:
                    assert st[k] == v
            assert len(st) == len(expect_keys)
            assert len(st) == st.size()

        def test_vals_items(self, st, expect_items):
            assert sorted(st.values()) == sorted([v for k, v in expect_items])
            assert sorted(st.items()) == sorted(expect_items)

    @pytest.mark.parametrize('ST', ALL_STS - NO_DELETE)
    class TestDelete:
        def test_delete_one(self, ST, cache, expect_keys):
            # Delete arbitrary key, starting with same table
            for k in expect_keys:
                t = ST(ITEMS, cache=cache)
                t[k]  # get item to ensure cache is used
                del t[k]
                assert k not in t
                assert len(t) == len(expect_keys) - 1
                assert sorted(t.keys()) == sorted(expect_keys - set(k))
                err_test(t, '__getitem__', k, err_type=KeyError)

        def test_alias(self, empty_st):
            st = empty_st
            st.put('A', 0)
            st.delete('A')
            assert not st.contains('A')
            assert st.is_empty

        def test_delete_all(self, st, expect_keys):
            test_keys = expect_keys.copy()
            N_expect = len(expect_keys)
            for k in st.keys():
                del st[k]
                N_expect -= 1
                test_keys -= set(k)
                assert st.size() == N_expect
                assert sorted(st.keys()) == sorted(test_keys)
            err_test(st, '__delitem__', 'Z', err_type=KeyError)
            assert st.is_empty


@pytest.mark.parametrize('cache', [True])
class TestCaching:
    @pytest.mark.parametrize('ST', SINGLEVAL_STS - NO_CACHE)
    class TestPutGet:
        def test_cache_new(self, empty_st):
            st = empty_st
            for k, v in ITEMS:
                st[k] = v
                if st.__class__ in [ArrayST, BinarySearchST]:
                    assert st._keys[st._cache] == k
                    assert st._vals[st._cache] == v
                else:
                    assert st._cache.key == k
                    assert st._cache.val == v

        def test_put_cache_existing(self, st):
            for k in st:
                st[k] = 56
                if st.__class__ in [ArrayST, BinarySearchST]:
                    assert st._keys[st._cache] == k
                    assert st._vals[st._cache] == 56
                else:
                    assert st._cache.key == k
                    assert st._cache.val == 56

        def test_get_cache_existing(self, st):
            for k in st:
                v = st[k]
                if st.__class__ in [ArrayST, BinarySearchST]:
                    assert st._keys[st._cache] == k
                    assert st._vals[st._cache] == v
                else:
                    assert st._cache.key == k
                    assert st._cache.val == v

    @pytest.mark.parametrize('ST', SINGLEVAL_STS - NO_CACHE - NO_DELETE)
    def test_delete_cache(self, st):
        for k in st.keys():
            st[k]  # __getitem__ to set the cache
            del st[k]
            assert st._cache is None
            assert k not in st


# Tests specific to a single data type
class TestSelfOrg:
    def test_selforg_nocache(self):
        """Test self-organizing search (Exercise 3.1.22)."""
        st = ArrayST(ITEMS, selforg=True, cache=False)
        rand_keys = rng.choice(st.keys(), size=st.size())
        for k in rand_keys:
            st[k]  # search for the key
            assert st.keys()[0] == k
            st[k]  # search again
            assert st._cost == 1

    def test_selforg_cache(self):
        """Test self-organizing search AND caching."""
        st = ArrayST(ITEMS, selforg=True, cache=True)
        rand_keys = rng.choice(st.keys(), size=st.size())
        for k in rand_keys:
            v = st[k]  # search for the key to set cache
            assert st._keys[0] == k
            assert st._keys[st._cache] == k
            assert st._vals[st._cache] == v
        del st[k]
        assert st._cache is None


# ---------- Test Ordered Operations ----------
def test_binary_integrity():
    st = BinarySearchST(ITEMS)
    st._assert_integrity()


@pytest.mark.parametrize('cache', [False, True])
class TestOrderedOps:
    @pytest.mark.parametrize('ST', ORDERED_STS - {ArrayBST})
    class TestPut:
        def test_empty_table(self, empty_st):
            assert empty_st.floor('A') is None
            assert empty_st.ceil('A') is None
            assert empty_st.rank('A') == 0

        def test_empty_raises(self, empty_st):
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
            assert st.ceil('Z') is None  # char > st.max()

        def test_range_search(self, st, expect_keys):
            # In-order traversal + range search
            assert st.keys() == sorted(expect_keys)
            assert st.size() == len(expect_keys)
            assert st.keys(lo='P') == list('PRSX')
            assert st.size(lo='P') == 4
            assert st.keys('F', 'P') == list('HLMP')
            assert st.size('F', 'P') == 4
            assert st.keys(hi='P') == list('ACEHLMP')
            assert st.size(hi='P') == 7

        def test_select_raises(self, st):
            err_test(st, 'select', -1, err_type=IndexError)  # too small
            err_test(st, 'select', 99, err_type=IndexError)  # too large

        # Rank for each key should be minimum index.
        # Select should return same key for multiple indices.
        def test_rank(self, st, expect_ranks, expect_keys):
            for i, c in zip(expect_ranks, sorted(expect_keys)):
                assert st.rank(c) == i

        def test_select(self, st, expect_keys):
            for i, c in enumerate(sorted(expect_keys)):
                assert st.select(i) == c

        # Ex 3.2.33
        def test_rankselect_inverse(self, st, expect_ranks, expect_keys):
            for k in st.keys():
                assert st.select(st.rank(k)) == k
            for i in expect_ranks:
                assert st.rank(st.select(i)) == i

    @pytest.mark.parametrize('ST', ((ORDERED_STS & SINGLEVAL_STS) - {ArrayBST}))
    def test_vals_items(self, st, expect_items):
        assert st.values() == [v for k, v in sorted(expect_items)]
        assert st.values('F', 'P') == [v for k, v in sorted(expect_items)[3:7]]
        assert st.items() == sorted(expect_items)
        assert st.items('F', 'P') == sorted(expect_items)[3:7]

    @pytest.mark.parametrize('ST', ORDERED_STS - NO_DELETE)
    class TestOrderedDelete:
        def test_delete_min(self, st, expect_keys):
            k = st.min()
            assert k == 'A'
            st.delete_min()  # remove 'A'
            assert st.min() == 'C'
            # Test updated ranks
            for i, c in enumerate(sorted(expect_keys - set(k))):
                assert st.select(i) == c
                assert st.rank(c) == i

        def test_delete_max(self, st, expect_keys):
            k = st.max()
            assert k == 'X'
            st.delete_max()  # remove 'X'
            assert st.max() == 'S'
            # Test updated ranks
            for i, c in enumerate(sorted(expect_keys - set(k))):
                assert st.select(i) == c
                assert st.rank(c) == i


# TODO every pair-wise comparison?
def test_comparisons():
    assert SequentialSearchST(ITEMS) == BinarySearchST(ITEMS)
    assert BinarySearchST(ITEMS) == SequentialSearchST(ITEMS)
    assert BinarySearchST(ITEMS) == BST(ITEMS)
    assert BST(ITEMS) == BinarySearchST(ITEMS)
    assert BST(ITEMS) == BST_nr(ITEMS)
    assert BST_nr(ITEMS) == BST(ITEMS)


# -----------------------------------------------------------------------------
#         Test MultiValSTs
# -----------------------------------------------------------------------------
@pytest.fixture
def expect_multi():
    return [
        ('A', [2, 8]),
        ('C', [4]),
        ('E', [1, 6, 12]),
        ('H', [5]),
        ('L', [11]),
        ('M', [9]),
        ('P', [10]),
        ('R', [3]),
        ('S', [0]),
        ('X', [7]),
    ]


@pytest.mark.parametrize('ST', MULTIVAL_STS)
@pytest.mark.parametrize('cache', [False, True])
class TestMultiVals:
    def test_size(self, st, expect_keys):
        assert st.size() == len(expect_keys)  # includes only unique keys

    def test_get(self, st, expect_multi):
        for k, v in expect_multi:
            assert st[k] in v

    def test_get_all(self, st, expect_multi):
        for k, v in expect_multi:
            assert st.get_all(k) == list(v)

    def test_put_iterable(self, st):
        st['X'] = [1, 2, 3]
        assert st['X'] in [7, [1, 2, 3]]
        assert st.get_all('X') == [7, [1, 2, 3]]
        st['Y'] = [4, 5, 6]
        assert st['Y'] in [[4, 5, 6]]
        assert st.get_all('Y') == [[4, 5, 6]]
        st['Y'] = 7
        assert st['Y'] in [[4, 5, 6], 7]
        assert st.get_all('Y') == [[4, 5, 6], 7]
        st['A'] = 'hello'
        assert st['A'] in [2, 8, 'hello']
        assert st.get_all('A') == [2, 8, 'hello']

    def test_delete(self, st):
        for k in st.keys():
            del st[k]
            assert k not in st
        assert st.is_empty

    def test_invert(self, st):
        assert st == invert(invert(st))


# =============================================================================
# =============================================================================
