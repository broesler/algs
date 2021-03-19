#!/usr/bin/env python3
# =============================================================================
#     File: test_basics.py
#  Created: 2021-03-02 09:02
#   Author: Bernie Roesler
#
"""
  Description: Unit tests for algs.basics.
"""
# =============================================================================

import numpy as np
import pytest
from random import shuffle
import string

from algs.basics import Bag, Stack, Queue, PriorityQueue, IndexPQ


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
        while True:
            getattr(container, op)(*args)  # call the method


class TestBag:
    def test_bag_methods(self):
        b = Bag()
        for i in range(10):
            b.add(i)
        assert b.size == 10
        assert len(b) == b.size
        assert not b.is_empty
        for i, x in enumerate(b):
            assert i == x

    def test_bag_stats(self):
        # Run some basic statistics from an interator of values
        b = Bag()
        scores = iter([100, 99, 101, 120, 98, 107, 109, 81, 101, 90])
        for s in scores:
            b.add(s)
        mean = 0.0
        std = 0.0
        N = b.size
        for x in b:
            mean += x / N
        for x in b:
            std += (x - mean)*(x - mean) / (N - 1)
        assert mean == 100.6
        np.testing.assert_almost_equal(std, 110.489, decimal=3)


class TestStack:
    def test_stack_methods(self):
        s = Stack()
        for i in range(5):
            s.push(i)
        assert s.size == 5
        assert not s.is_empty
        assert 4 == s.peek()
        assert 4 == s.pop()
        # Test iteration -- pop should be in reverse order
        for i, item in zip([3, 2, 1, 0], s):
            assert i == item
        err_test(s, 'pop')


class TestQueue:
    def test_queue_methods(self):
        q = Queue(['A', 'B', 'C'])
        q.enqueue('D')
        assert q.size == 4
        assert not q.is_empty
        assert 'A' == q.peek()
        assert 'A' == q.dequeue()
        # Elements should be in forwards order
        for c, item in zip(['B', 'C', 'D'], q):
            assert c == item
        err_test(q, 'dequeue')


@pytest.fixture
def idx_s():
    """Shuffled alphabet data with indices"""
    return list(range(len(string.ascii_uppercase)))


@pytest.fixture
def idx(idx_s):
    idx = idx_s.copy()
    shuffle(idx)
    return idx


@pytest.fixture
def data(idx):
    return list(string.ascii_uppercase[i] for i in idx)


class TestPQ:
    def test_maxpq_methods(self, data):
        pq = PriorityQueue(data, kind='max')
        assert not pq.is_empty
        assert pq.size == 26
        assert 'Z' == pq.peek()
        assert 'Z' == pq.dequeue()
        assert 'Y' == pq.dequeue()
        assert 'X' == pq.dequeue()
        assert 'W' == pq.peek()
        for c in ['X', 'Y', 'Z']:
            pq.enqueue(c)
        # implicitly test iteration
        assert ''.join(pq) == string.ascii_uppercase[::-1]
        err_test(pq, 'dequeue')

    def test_minpq_methods(self, data):
        pq = PriorityQueue(data, kind='min')
        assert 'A' == pq.dequeue()
        assert 'B' == pq.dequeue()
        assert 'C' == pq.dequeue()
        assert 'D' == pq.peek()
        for c in ['A', 'B', 'C']:
            pq.enqueue(c)
        # implicitly test iteration
        assert ''.join(pq) == string.ascii_uppercase


@pytest.fixture
def pq(idx, data):
    return IndexPQ(zip(idx, data), kind='min')


class TestIndexPQ:
    def test_indexpq_methosd(self, idx_s, pq):
        assert len(pq) == 26
        assert (0, 'A') == pq.dequeue()
        assert (1, 'B') == pq.dequeue()
        assert (2, 'C') == pq.dequeue()
        assert len(pq) == 23
        assert (3, 'D') == pq.peek()
        for i, c in [(0, 'A'), (1, 'B'), (2, 'C')]:
            pq.enqueue(i, c)
        assert list(pq.keys()) == idx_s
        assert ''.join(pq.values()) == string.ascii_uppercase

    def test_indexpq_change_item(self, idx_s, pq):
        pq[0] = 'ZZZ'
        assert 0 in pq
        assert list(pq.keys()) == idx_s[1:] + [0]
        assert ''.join(pq.values()) == string.ascii_uppercase[1:] + 'ZZZ'
        pq[0] = 'A'
        assert 0 in pq
        assert list(pq.keys()) == idx_s
        assert ''.join(pq.values()) == string.ascii_uppercase

    def test_indexpq_delete_item(self, idx_s, pq):
        i = 0  # removes (0, 'A')
        item = pq[i]  # store value for later
        del pq[i]
        assert i not in pq
        assert list(pq.keys()) == idx_s[:i] + idx_s[i+1:]
        assert ''.join(pq.values()) == (string.ascii_uppercase[:i]
                                        + string.ascii_uppercase[i+1:])
        # Re-add item for completeness
        pq[i] = item

    def test_indexpq_internals(self, pq):
        for i in range(len(pq._pq)-1):
            assert pq._pq[pq._qp[i]] == i

    def test_indexpq_equality(self, idx, data):
        pq1 = IndexPQ(zip(idx, data), kind='min')
        pq2 = IndexPQ(zip(idx, data), kind='min')
        assert pq1 == pq2
        del pq1, pq2

    def test_indexpq_copy(self, pq):
        pq_copy = pq.copy()
        assert pq_copy == pq

    def test_indexpq_fromkeys(self, idx, pq):
        pq_fromkeys = pq.fromkeys(idx)
        assert pq_fromkeys.keys() == pq.keys()

# =============================================================================
# =============================================================================
