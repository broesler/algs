#!/usr/bin/env python3
# =============================================================================
#     File: perfect_hash.py
#  Created: 2022-05-25 13:51
#   Author: Bernie Roesler
#
"""
Exercise 3.4.4 Perfect Hashing.
"""
# =============================================================================

def _hash(k, a=1, M=1):
    """The hash function for the `k`th letter of the alphabet."""
    return (a * (ord(k) - ord('A'))) % M


def perfect_hash(s):
    """Return the parameters for a perfect hash of string `s`."""
    N = len(s)
    for M in range(1, 1000):
        for a in range(1000):
            hashes = [_hash(k, a, M) for k in s]
            if len(hashes) == len(set(hashes)):
                return a, M


if __name__ == "__main__":
    keys = 'SEARCHXMPL'  # unique keys
    a, M = perfect_hash(keys)
    print((a, M))
    # Confirm it works
    print(sorted([_hash(k, a, M) for k in keys]))

# =============================================================================
# =============================================================================
