#!/usr/bin/env python3
# =============================================================================
#     File: parenthesis.py
#  Created: 2022-05-27 13:42
#   Author: Bernie Roesler
#
"""
Exercise 1.3.4 Determine if a series of parentheses are in order.
"""
# =============================================================================

from algs.basics import Stack

a = list('[()]{}{[()()]()}')  # True
b = list('[(])')              # False


def parentheses(a):
    """Return True if the parentheses in `a` are properly paired."""
    pairs = dict({'[': ']', '(': ')', '{': '}'})
    opens = pairs.keys()
    closes = pairs.values()
    s = Stack()
    for c in a:
        if c in opens:
            s.push(c)
        elif c in closes:
            x = s.pop()
            if c != pairs[x]:
                return False
        # else: skip over any other characters
    return True


assert parentheses(a)
assert not parentheses(b)

# =============================================================================
# =============================================================================
