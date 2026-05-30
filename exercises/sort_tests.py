#!/usr/bin/env python3
# ==============================================================================
#     File: test_sort.py
#  Created: 2019-03-15 00:28
#   Author: Bernie Roesler
# ==============================================================================

"""Test sorting functions with basic inputs."""

import random
import string

from algs.sort import (
    bubble_sort,
    heap_sort,
    insertion_sort,
    is_sorted,
    mergesort,
    mergesort_BU,
    qsort,
    qsort0,
    qsort1,
    qsort2,
    quicksort0,
    quicksort0r,
)


class TestRunner:
    """Class to run tests and keep track of results."""

    def __init__(self):
        self.tests = 0
        self.fails = 0

    def should_be(self, a, b):
        """Test a condition."""
        self.tests += 1
        try:
            assert a == b
        except AssertionError as e:
            self.fails += 1
            print(f"[{test_name}]: Got: {a}, Expected: {b}")
            raise e

    def print_summary(self):
        """Print a summary of the test results."""
        if self.fails > 0:
            print(f"{self.fails}/{self.tests} tests failed")
        else:
            print(f"All {self.tests} tests passed!")


# Define test cases
ints = [8, 4, 3, 2, 1, 7, 6, 0, 5, 9]
# ints = [6, 8, 3, 9, 6, 6, 2, 1, 6, 0, 7, 4]  # repeated keys
chrs = list('SORTEXAMPLE')

s = string.ascii_uppercase
strs = [s[i : i + 3] for i in range(0, len(s), 3)]
random.shuffle(strs)

test_As = [(ints, sorted(ints)), (chrs, sorted(chrs)), (strs, sorted(strs))]

sort_funs = [
    bubble_sort,
    insertion_sort,
    mergesort,
    mergesort_BU,
    quicksort0,
    quicksort0r,
    qsort0,
    qsort1,
    qsort2,
    qsort,
    heap_sort,
]

# ------------------------------------------------------------------------------
#        Run general sorting algorithm tests
# ------------------------------------------------------------------------------
runner = TestRunner()

for A, S in test_As:
    runner.should_be(is_sorted(S), True)
    for sort in sort_funs:
        test_name = sort.__name__
        runner.should_be(sort([]), [])  # empty list
        runner.should_be(sort([0]), [0])  # single element list
        runner.should_be(sort([1, 1, 1]), [1, 1, 1])  # all equal
        runner.should_be(sort(A) is not A, True)  # return a copy
        runner.should_be(sort(list(A)), S)  # randomized A
        runner.should_be(sort(list(S)), S)  # sorted list
        runner.should_be(sort(list(S[::-1])), S)  # reverse sorted list

runner.print_summary()

# ==============================================================================
# ==============================================================================
