#!/usr/bin/env python3
# =============================================================================
#     File: kgrams.py
#  Created: 2022-06-02 00:55
#   Author: Bernie Roesler
#
"""
Print a sorted list of k-grams in a string.
"""
# =============================================================================

from pathlib import Path
from tqdm import tqdm

from algs.search.set import MultiValST


def kgrams(a, k=1, verbose=False):
    """Return a sorted list of k-grams and their positions in the string."""
    st = MultiValST()
    iters = range(len(a) - k + 1)
    if verbose:
        iters = tqdm(iters)
    for i in iters:
        c = a[i:i+k]
        st[c] = i
    return st


if __name__ == '__main__':
    a = 'AACTBCAAXYZCT'
    st = kgrams(a, k=2)
    print(sorted(st.items()))

    filename = Path('../data/ecoli.txt')
    with open(filename, 'r') as fp:
        a = fp.readline().strip()[:1000]
    st = kgrams(a, k=2)
    print(sorted(st.items()))

# =============================================================================
# =============================================================================
