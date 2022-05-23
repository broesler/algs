#!/usr/bin/env python3
# =============================================================================
#     File: string_hash.py
#  Created: 2022-05-23 11:04
#   Author: Bernie Roesler
#
"""
Exercise 3.4.23 string hashing with bad constants.

Show that any permutation of the characters hashes to the same value.
"""
# =============================================================================

from random import shuffle

from algs.search.hash import java_hash

N = 100  # number of permutations to test (len(test_str)! exist)
test_str = 'SEARCHEXAMPLE'

ords = [ord(c) for c in test_str]

def bad_hash(k):
    """The hash function."""
    R = 56
    M = 55
    return java_hash(test_str, R=R) % M


h = bad_hash(test_str)  # == 183

# Test on N permutations of the string
a = list(test_str)
for _ in range(N):
    shuffle(a)
    assert bad_hash(a) == h


# =============================================================================
# =============================================================================
