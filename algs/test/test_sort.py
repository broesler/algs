#!/usr/bin/env python3
#==============================================================================
#     File: test_sort.py
#  Created: 2019-03-15 00:28
#   Author: Bernie Roesler
#
"""
  Description: Test sorting functions with basic inputs.
"""
#==============================================================================

import string
import random

from algs.sort import is_sorted, bubble_sort, insertion_sort, mergesort, \
                      mergesort_BU, qsort, heap_sort, \
                      quicksort0, quicksort0r, qsort0, qsort1, qsort2

def should_be(a, b):
    """Test a condition."""
    global tests, fails
    tests += 1
    try:
        assert a == b
    except AssertionError as e:
        fails += 1
        print(f"[{test_name}]: Got: {a}, Expected: {b}")
        raise e

# Define test cases
ints = [8, 4, 3, 2, 1, 7, 6, 0, 5, 9]
# ints = [6, 8, 3, 9, 6, 6, 2, 1, 6, 0, 7, 4]  # repeated keys
chrs = list('SORTEXAMPLE')

s = string.ascii_uppercase
strs = [s[i:i+3] for i in range(0, len(s), 3)]
random.shuffle(strs)

test_As = [(ints, sorted(ints)),
           (chrs, sorted(chrs)),
           (strs, sorted(strs))]

sort_funs = [bubble_sort, insertion_sort, mergesort, mergesort_BU,
             quicksort0, quicksort0r, qsort0, qsort1, qsort2, qsort,
             heap_sort]

#------------------------------------------------------------------------------
#        Run general sorting algorithm tests
#------------------------------------------------------------------------------
tests = 0
fails = 0

for A, S in test_As:
    should_be(is_sorted(S), True)
    for sort in sort_funs:
        test_name = sort.__name__
        should_be(sort([]), [])                # empty list
        should_be(sort([0]), [0])              # single element list
        should_be(sort([1, 1, 1]), [1, 1, 1])  # all equal
        should_be(sort(A) is not A, True)      # return a copy
        should_be(sort(list(A)), S)            # randomized A
        should_be(sort(list(S)), S)            # sorted list
        should_be(sort(list(S[::-1])), S)      # reverse sorted list

if fails > 0:
    print(f"{fails}/{tests} tests failed")
else:
    print(f"All {tests} tests passed!")

#==============================================================================
#==============================================================================
