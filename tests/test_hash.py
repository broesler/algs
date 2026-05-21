#!/usr/bin/env python3
# =============================================================================
#     File: test_hash.py
#  Created: 2022-06-30 12:35
#   Author: Bernie Roesler
#
"""
  Description: Unit tests for hash table operations not covered by test_search.
"""
# =============================================================================

import numpy as np
import pytest

from algs.search.hash import (SeparateChainingHashST,
                              SeparateChainingLiteHashST, LinearProbingHashST,
                              LazyLinearProbingHashST, DoubleProbingHashST,
                              DoubleHashingHashST, CuckooHashST, LIFOHashST)

# Exercise 3.4.1
KEYS = 'EASYQUTION'
ITEMS = tuple((c, i) for i, c in enumerate(KEYS))


# Define custom has functions
def _hash_code(k, R=11):
    """Return the hash code for the `k`th letter of the alphabet."""
    return R*(ord(k) - ord('A'))


def _hash(self, k, **kwargs):
    """Implement modular hashing in a table of size `M`."""
    return _hash_code(k, **kwargs) % self.M


# Override _hash function with custom subclasses
class MySeparateChainingHashST(SeparateChainingHashST):
    _hash = _hash


# Repeat with SeparateChainingLiteHashST
class MySeparateChainingLiteHashST(SeparateChainingLiteHashST):
    _hash = _hash


# Exercise 3.4.10 (a)
# Override _hash function with custom subclass
class MyLinearProbingHashST(LinearProbingHashST):
    _hash = _hash


class MyDoubleProbingHashST(DoubleProbingHashST):
    _hash = _hash  # R = 11

    def _hash_b(self, k):
        return self._hash(k, R=7)


class MyDoubleHashingHashST(DoubleHashingHashST):
    _hash = _hash  # R = 11

    def _hash_b(self, k):
        return (self._hash(k, R=17) % self.M) + 1  # must be non-zero


class MyCuckooHashST(CuckooHashST):
    class HashArrayA(CuckooHashST.HashArrayA):
        hash = _hash  # R = 11

    class HashArrayB(CuckooHashST.HashArrayB):
        def hash(self, k):
            return _hash_code(k, R=17) % self.M


class MyLIFOHashST(LIFOHashST):
    _hash = _hash


@pytest.fixture
def sch():
    return MySeparateChainingHashST(ITEMS, M=5)


@pytest.fixture
def scl():
    return MySeparateChainingLiteHashST(ITEMS, M=5)


# -----------------------------------------------------------------------------
#         Tests
# -----------------------------------------------------------------------------
def test_sch_keys(sch):
    sch._validate_size()
    assert sch.keys() == list('UAQNISOTYE')


def test_sch_cost(sch):
    # Unsuccessful search
    try:
        del sch['X']
    except KeyError:
        pass
    assert sch._cost == 4  # _hash('X') == 3, len(st[3]) == 3 + 1 = 4


def test_scl_keys(scl):
    assert scl.keys() == list('UAQNISOTYE')


# Exercise 3.4.3
def test_scl_delete_later_than(scl):
    scl.delete_later_than(5)  # corresponds to 'U'
    assert all([x.N_before <= 5 for x in scl._nodes()])
    assert all([k in list('EASYQU') for k in scl.keys()])


def test_lph():
    st = MyLinearProbingHashST(ITEMS, M=16, resize=False)
    assert st.keys() == list('AQTSYIOEUN')
    assert np.allclose(st._cluster_lengths(), [1, 3, 2, 4])


# Exercise 3.4.10 (b)
def test_lph_small():
    st = MyLinearProbingHashST(ITEMS, M=10, resize=False)
    assert st.keys() == list('AUINEYQOST')
    assert np.allclose(st._cluster_lengths(), [10])


# Exercise 3.4.11
def test_lph_resize():
    st = MyLinearProbingHashST(ITEMS, M=4, resize=True)
    assert st.keys() == list('ASYENQTIOU')


def test_lazy_delete():
    st = LazyLinearProbingHashST(ITEMS)
    M = st.M
    thresh = M // 8  # N value for resize
    for i, k in zip(range(len(KEYS) - thresh - 1), KEYS):
        del st[k]                # lazy delete by setting val to None
        idx = st._keys.index(k)  # linear search for internal index
        assert st._vals[idx] is None
        assert st.M == M
        assert k not in st       # test `__getitem__`

    del st[KEYS[i+1]]  # force a resize
    assert st.M == M // 2

    # Test actual deletion of keys
    for i, k in zip(range(len(KEYS) - thresh - 1), KEYS):
        assert k not in st._keys


# Exercise 3.4.27
def test_dph():
    st = MyDoubleProbingHashST(ITEMS, M=3)
    assert st.keys() == list('YSANOTEIUQ')


# Exercise 3.4.28
def test_dhh():
    st = MyDoubleHashingHashST(ITEMS, M=11)
    assert st.keys() == list('AYOESITQNU')


# Exercise 3.4.31
def test_cht():
    # choose M = next_prime(2*len(keys))
    st = MyCuckooHashST(ITEMS, M=23, resize=False)
    assert st.keys() == list('ATNYUSQOIE')


# test resizing
def test_cht_resize():
    st = MyCuckooHashST(ITEMS)
    assert st.keys() == list('AYOESITQNU')


# Web Exercise 16
def test_lifo():
    st = MyLIFOHashST(ITEMS, M=16, resize=False)
    assert st.keys() == list('QTASIYOUEN')

# =============================================================================
# =============================================================================
