#!/usr/bin/env python3
# =============================================================================
#     File: test_search.py
#  Created: 2021-03-02 09:18
#   Author: Bernie Roesler
#
"""
  Description: Unit tests for algs.search.
"""
# =============================================================================

import numpy as np

from algs.search import SequentialSearchST, BinarySearchST, ArrayST, \
                        BST, BST_nr, ThreadedST, ThreadedST_nr, ArrayBST, \
                        RedBlackBST

# TODO write Pytest classes/functions
# Ex 3.1.29 (and then some!)

rng = np.random.default_rng(seed=565656)

# Define test counts
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
    global tests, fails
    tests += 1
    try:
        getattr(container, op)(*args)  # call the method
    except err_type:
        return
    except Exception as err:
        fails += 1
        print(f"Raised: {repr(err)}, Expected: {err_type}")
        raise err
    else:
        fails += 1
        print(f"No error raised! Expected: {err_type}")
        raise


# Prepare test data
test_str = 'SEARCHEXAMPLE'
test_set = set(test_str)
data = [(c, i) for i, c in enumerate(test_str)]
data_set = data.copy()
data_set.remove(('E', 1))
data_set.remove(('A', 2))
data_set.remove(('E', 6))

# ---------- Test All STs ----------
for ST in [SequentialSearchST, ArrayST, BinarySearchST, BST, BST_nr,
           ThreadedST, ThreadedST_nr, ArrayBST, RedBlackBST]:
    st = ST(cache=False)
    should_be(st.size, 0)
    should_be(st.is_empty, True)
    should_be(st.keys(),   [])
    should_be(st.values(), [])
    should_be(st.items(),  [])

    st = ST(data, cache=False)
    for k, v in data:
        should_be(k in st, True)
        if k == 'E' or k == 'A':
            should_be(st[k], max([val for key, val in data if key == k]))
        else:
            should_be(st[k], v)

    should_be(len(st), len(test_set))  # test __len__
    should_be(len(st), st.size)
    # st.keys() not guaranteed in order, so these tests are weak
    should_be(sorted(st.keys()), sorted(test_set))
    should_be(sorted(st.values()), sorted([v for k, v in data_set]))
    should_be(sorted(st.items()), sorted(data_set))

    err_test(st, '__getitem__', 'Z', err_type=KeyError)

    # delete cut-off here
    if st.__class__ is ArrayBST or st.__class__ is RedBlackBST:
        continue

    test_keys = test_set.copy()
    for k in st:
        del st[k]
        test_keys -= set(k)
        should_be(sorted(st.keys()), sorted(test_keys))

    # Test caching
    st = ST(data, cache=True)
    for k in st:
        v = st[k]                       # __getitem__
        should_be(st._cache.key, k)
        should_be(st._cache.val, v)
        st[k] = 56                       # __setitem__
        should_be(st._cache.key, k)
        should_be(st._cache.val, 56)
    del st[k]
    should_be(st._cache, None)

# Test self-organizing search (Exercise 3.1.22)
st = ArrayST(data, selforg=True, cache=False)
rand_keys = rng.choice(st.keys(), size=st.size)
for k in rand_keys:
    st[k]                       # search for the key
    should_be(st.keys()[0], k)  # should get moved to front
    st[k]                       # search again
    should_be(st._cost, 1)      # test cost

# Test self-organizing search AND caching
st = ArrayST(data, selforg=True, cache=True)
rand_keys = rng.choice(st.keys(), size=st.size)
for k in rand_keys:
    st[k]                       # search for the key
    should_be(st.keys()[0], k)  # should get moved to front
    should_be(st._cache.key, k)
del st[k]
should_be(st._cache, None)

# ---------- Test Ordered Operations ----------
for ST in [BinarySearchST, BST, BST_nr, ThreadedST, ThreadedST_nr,
           RedBlackBST]:
    for cache in [False, True]:
        t = ST(cache=cache)
        # Test bad input type
        err_test(t, '__init__', list('BADEXAMPLE'), err_type=ValueError)
        # Test empty table operations
        should_be(t.size, 0)
        should_be(t.is_empty, True)
        should_be(t.keys(),   [])
        should_be(t.values(), [])
        should_be(t.items(),  [])
        err_test(t, '__getitem__', 'A', err_type=KeyError)
        err_test(t, 'min', err_type=KeyError)
        err_test(t, 'max', err_type=KeyError)
        err_test(t, 'delete_min', err_type=KeyError)
        err_test(t, 'delete_max', err_type=KeyError)
        should_be(t.floor('A'),  None)
        should_be(t.ceil('A'),  None)
        should_be(t.rank('A'),  0)
        err_test(t, 'select', 0, err_type=IndexError)

        # Test insert/get single node
        t['A'] = 0
        should_be(t['A'], 0)

        # Test construction by list of tuples
        t = ST(data, cache=cache)

        if isinstance(t, BinarySearchST):
            should_be(t._assert_integrity(), None)

        # Binary Search Tree:
        #  height depth
        #  5      0           S
        #                    / \
        #  4      1         E   X
        #                /    \
        #  3      2     A      R
        #                \    /
        #  2      3       C  H
        #                     \
        #  1      4            M
        #                     / \
        #  0      5          L   P

        should_be(len(t), len(test_set))  # test __len__
        should_be(len(t), t.size)

        for k, v in data:
            # test __contains__
            should_be(k in t, True)

            # test __getitem__
            if k == 'E' or k == 'A':
                should_be(t[k], max([v for key, v in data if key == k]))
            else:
                should_be(t[k], v)

        # Test __contains__ for item *not* in table
        should_be('B' in t, False)

        should_be(t.min(), 'A')
        should_be(t.max(), 'X')

        should_be(t.floor('H'), 'H')  # key in table
        should_be(t.ceil('H'),  'H')
        should_be(t.floor('Q'), 'P')  # key not in table
        should_be(t.ceil('Q'),  'R')
        should_be(t.floor(chr(ord('A') - 1)), None)  # char < t.min()
        should_be(t.ceil('Z'), None)                 # char > t.max()

        # Select and Rank tests
        err_test(t, 'select', -1, err_type=IndexError)  # too small
        for i, c in enumerate(sorted(test_set)):
            should_be(t.select(i), c)
            should_be(t.rank(c), i)
        err_test(t, 'select', 99, err_type=IndexError)  # too large

        # Ex 3.2.33
        for i in range(t.size):
            should_be(t.rank(t.select(i)), i)

        for k in t.keys():
            should_be(t.select(t.rank(k)), k)

        # BST-specific tests
        if isinstance(t, BST) and t.__class__ is not RedBlackBST:
            should_be(t.pre_order(),   list('SEACRHMLPX'))
            should_be(t.in_order(),    list('ACEHLMPRSX'))
            should_be(t.post_order(),  list('CALPMHREXS'))
            should_be(t.level_order(), list('SEXARCHMLP'))
            should_be(t.height_r(), 5)  # recursive method
            should_be(t.height, 5)      # Node attribute method
            should_be(t.isBST(), True)
            should_be(t.internal_path_length_r(), 26)
            should_be(t.internal_path_length, 26)
            del t['H']  # remove node with single child
            should_be(t.height_r(), 4)  # recursive method
            should_be(t.height, 4)      # Node attribute method
            should_be(t.internal_path_length, 20)
            t = ST(data, cache=cache)
            t['G'] = 6
            should_be(t.internal_path_length, 30)
            del t['H']  # remove node with two children
            should_be(t.internal_path_length, 25)

        # In-order traversal + range search
        t = ST(data, cache=cache)
        should_be(list(t.keys()), sorted(test_set))
        should_be(list(t.keys(lo='P')), list('PRSX'))
        should_be(list(t.keys('F', 'P')), list('HLMP'))  # subset of keys
        should_be(list(t.keys(hi='P')), list('ACEHLMP'))
        should_be(list(t.values()), [v for k, v in sorted(data_set)])
        should_be(list(t.values('F', 'P')),
                  [v for k, v in sorted(data_set)[3:7]])
        should_be(list(t.items()), sorted(data_set))
        should_be(list(t.items('F', 'P')), sorted(data_set)[3:7])

        # Test deletion and reinsertion
        k, v = t.min(), t[t.min()]
        t.delete_min()  # remove 'A'
        should_be(t.min(), 'C')
        # Test updated ranks
        for i, c in enumerate(sorted(test_set - set(k))):
            should_be(t.select(i), c)
            should_be(t.rank(c), i)
        t[k] = v  # replace value

        k, v = t.max(), t[t.max()]
        t.delete_max()  # remove 'X'
        should_be(t.max(), 'S')
        # Test updated ranks
        for i, c in enumerate(sorted(test_set - set(k))):
            should_be(t.select(i), c)
            should_be(t.rank(c), i)
        t[k] = v  # replace value

        # Delete arbitrary key, starting with same tree
        for k in test_set:
            t = ST(data, cache=cache)
            v = t[k]
            del t[k]
            should_be(len(t), len(test_set)-1)
            err_test(t, '__getitem__', k, err_type=KeyError)

    # Test BST internal structure
    if isinstance(t, BST) and t.__class__ is not RedBlackBST:
        t = ST(data)  # reset tree
        # delete the root (default deletion)
        should_be(t._root.key, 'S')
        del t['S']
        should_be(len(t), len(test_set)-1)
        should_be(t._root.key, 'X')
        should_be(t._root.left.key, 'E')
        should_be(t._root.right, None)
        # Test Hibbard deletion option
        t = ST(data, delete_method='Hibbard')
        should_be(t._root.key, 'S')
        del t['S']
        should_be(t._root.key, 'X')
        should_be(t._root.left.key, 'E')
        should_be(t._root.right, None)
        # Test predecessor deletion option
        t = ST(data, delete_method='Hibbard_p')
        should_be(t._root.key, 'S')
        del t['S']
        should_be(t._root.key, 'R')
        should_be(t._root.left.key, 'E')
        should_be(t._root.right.key, 'X')

# Test comparisons between objects (in *both* directions)
should_be(SequentialSearchST(data), BinarySearchST(data))
should_be(BinarySearchST(data), SequentialSearchST(data))
should_be(BinarySearchST(data), BST(data))
should_be(BST(data), BinarySearchST(data))
should_be(BST(data), BST_nr(data))
should_be(BST_nr(data), BST(data))


# -----------------------------------------------------------------------------
#         Test ThreadedST methods
# -----------------------------------------------------------------------------
def test_threads(t, test_set):
    """Test that the next/prev attributes are set properly."""
    keys = sorted(test_set)
    for i, k in enumerate(keys[:-1]):
        should_be(t.next(k), keys[i+1])
    should_be(t.next(keys[-1]), None)

    keys = sorted(test_set, reverse=True)
    for i, k in enumerate(keys[:-1]):
        should_be(t.prev(k), keys[i+1])
    should_be(t.prev(keys[-1]), None)


for ST in [ThreadedST, ThreadedST_nr]:
    t = ST(data)
    test_threads(t, test_set)

    k, v = t.min(), t[t.min()]
    t.delete_min()  # remove 'A'
    test_threads(t, sorted(test_set - set(k)))
    t[k] = v

    k, v = t.max(), t[t.max()]
    t.delete_max()  # remove 'X'
    test_threads(t, sorted(test_set - set(k)))
    t[k] = v

    # Delete arbitrary key, starting with same tree
    for k in test_set:
        t = ST(data)
        v = t[k]
        del t[k]
        test_threads(t, sorted(test_set - set(k)))

# Summary
if fails > 0:
    print(f"{fails}/{tests} tests failed")
else:
    print(f"All {tests} tests passed!")

# =============================================================================
# =============================================================================
