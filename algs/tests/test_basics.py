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

# TODO move to proper Pytest functions/classes
import string
import numpy as np
from random import shuffle

from algs.basics import Bag, Stack, Queue, PriorityQueue, IndexPQ

tests = fails = 0


def should_be(a, b, name=None, verbose=False):
    """Test a condition."""
    global tests, fails
    tests += 1
    try:
        assert a == b
        if verbose:
            print(f"[{name}]: Got: {a}, Expected: {b}")
    except AssertionError as e:
        fails += 1
        print(f"[{name}]: Got: {a}, Expected: {b}")
        raise e


def err_test(container, op, err_type=IndexError):
    """Test for raising a given error type.

    Parameters
    ----------
    container : list-like container data type
    op : str
        attribute name of method to test
    err_type : Exception, optional
        error type that object is expected to raise

    Returns
    -------
    None
    """
    while True:
        try:
            getattr(container, op)()  # call the method
        except err_type:
            return
        except Exception as err:
            raise Exception(f'Improper error thrown: {repr(err)}')


# Test Bag
b = Bag()
for i in range(10):
    b.add(i)
should_be(b.size, 10)
should_be(b.is_empty, False)
for i, x in enumerate(b):
    should_be(i, x)

# Run some basic statistics from an interator of values
b = Bag()
scores = iter([100, 99, 101, 120, 98, 107, 109, 81, 101, 90])  # ~ StdIn
for s in scores:
    b.add(s)
mean = 0.0
std = 0.0
N = b.size
for x in b:
    mean += x / N
for x in b:
    std += (x - mean)*(x - mean) / (N - 1)
should_be(mean, 100.6)
np.testing.assert_almost_equal(std, 110.489, decimal=3)

# Test Stack
s = Stack()
for i in range(5):
    s.push(i)
should_be(s.size, 5)
should_be(s.is_empty, False)
should_be(4, s.peek())
should_be(4, s.pop())
# Test iteration -- pop should be in reverse order
for i, item in zip([3, 2, 1, 0], s):
    should_be(i, item)
# Test for pop
err_test(s, 'pop')

# Test Queue
q = Queue(['A', 'B', 'C'])
q.enqueue('D')
should_be(q.size, 4)
should_be(q.is_empty, False)
should_be('A', q.peek())
should_be('A', q.dequeue())
# Elements should be in forwards order
for c, item in zip(['B', 'C', 'D'], q):
    should_be(c, item)
# Test dequeue error
err_test(q, 'dequeue')

# Shuffled alphabet data with indices
data_s = string.ascii_uppercase
idx_s = list(range(len(data_s)))
idx = idx_s.copy()
shuffle(idx)
data = [data_s[i] for i in idx]

# Test maxPQ
pq = PriorityQueue(data, kind='max')
should_be(pq.is_empty, False)
should_be(pq.size, 26)
should_be('Z', pq.peek())
should_be('Z', pq.dequeue())
should_be('Y', pq.dequeue())
should_be('X', pq.dequeue())
should_be('W', pq.peek())
for c in ['X', 'Y', 'Z']:
    pq.enqueue(c)
# implicitly test iteration
should_be(''.join(pq), string.ascii_uppercase[::-1])
# Test dequeue error
err_test(pq, 'dequeue')

# Test MinPQ
pq = PriorityQueue(data, kind='min')
should_be('A', pq.dequeue())
should_be('B', pq.dequeue())
should_be('C', pq.dequeue())
should_be('D', pq.peek())
for c in ['A', 'B', 'C']:
    pq.enqueue(c)
# implicitly test iteration
should_be(''.join(pq), string.ascii_uppercase)

# Test IndexMinPQ
pq = IndexPQ(zip(idx, data), kind='min')
should_be(len(pq), 26)
should_be((0, 'A'), pq.dequeue())
should_be((1, 'B'), pq.dequeue())
should_be((2, 'C'), pq.dequeue())
should_be(len(pq), 23)
should_be((3, 'D'), pq.peek())
for i, c in [(0, 'A'), (1, 'B'), (2, 'C')]:
    pq.enqueue(i, c)
should_be(list(pq.keys()), idx_s)
should_be(''.join(pq.values()), string.ascii_uppercase)

# Test `change` item
pq[0] = 'ZZZ'
should_be(0 in pq, True)
should_be(list(pq.keys()), idx_s[1:] + [0])
should_be(''.join(pq.values()), string.ascii_uppercase[1:] + 'ZZZ')
pq[0] = 'A'
should_be(0 in pq, True)
should_be(list(pq.keys()), idx_s)
should_be(''.join(pq.values()), string.ascii_uppercase)

# Test 'delete' item
i = 0  # removes (0, 'A')
item = pq[i]  # store value for later
del pq[i]
should_be(i not in pq, True)
should_be(list(pq.keys()), idx_s[:i] + idx_s[i+1:])
should_be(''.join(pq.values()),   string.ascii_uppercase[:i]
                                + string.ascii_uppercase[i+1:])

# Re-add item for completeness
pq[i] = item

# Internal checks
for i in range(len(pq._pq)-1):
    should_be(pq._pq[pq._qp[i]], i)

# Equality checks
pq1 = IndexPQ(zip(idx, data), kind='min')
pq2 = IndexPQ(zip(idx, data), kind='min')
should_be(pq1, pq2)
del pq1, pq2

# Copy check
pq_copy = pq.copy()
should_be(pq_copy, pq)

pq_fromkeys = pq.fromkeys(idx)

# Summary
if fails > 0:
    print(f"{fails}/{tests} tests failed")
else:
    print(f"All {tests} tests passed!")


# =============================================================================
# =============================================================================
