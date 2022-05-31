#!/usr/bin/env python3
# =============================================================================
#     File: set.py
#  Created: 2022-05-30 19:34
#   Author: Bernie Roesler
#
"""
Implements Set and HashSet APIs using symbol tables. See section 3.5.
"""
# =============================================================================

from algs import SymbolTable, RedBlackBST, LinearProbingHashST


class HashSet(LinearProbingHashST):
    __doc__ = f"""Implements a set using a linear probing hash table.
                {SymbolTable.__doc__}"""

    def __init__(self, keys=None):
        super().__init__()
        keys = keys or []
        for k in keys:
            self.__setitem__(k)

    def __setitem__(self, k):
        super().__setitem__(k, v=None)

    def __getitem__(self, k):
        raise TypeError('HashSet object is not subscriptable!')


if __name__ == "__main__":
    a = HashSet(list('abcde'))
    print(a)

# =============================================================================
# =============================================================================
