#!/usr/bin/env python3
# =============================================================================
#     File: circshift.py
#  Created: 2022-06-08 12:38
#   Author: Bernie Roesler
#
"""
Exercise 1.2.6: Detect a circular shift in a string.
"""
# =============================================================================

def is_circshift(a, b):
    """Return True if `a` and `b` are circularly shifted from each other."""
    if len(a) != len(b):
        return False
    return a in (b + b)

if __name__ == "__main__":
    a = 'ACTGACG'
    b = 'TGACGAC'
    c = 'XYZABCD'
    assert is_circshift(a, b)
    assert not is_circshift(a, c)

# =============================================================================
# =============================================================================
