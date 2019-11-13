#!/usr/bin/env python3
# =============================================================================
#     File: test_search.py
#  Created: 2019-11-06 21:53
#   Author: Bernie Roesler
#
"""
  Description: Create FrequencyCounter driver to test search classes.
"""
# =============================================================================

import mmap
import os
import pickle
import re

from tqdm import tqdm

from algs.search import SequentialSearchST, BinarySearchST

pat = re.compile(r"[a-zA-Z']+")  # split on non-alphabet chars and underscores

def get_num_lines(filename):
    """Scan through file to count the number of lines."""
    fp = open(filename, 'r+')
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines


def frequency_counter(ST, filename, minlen=1):
    # Build symbol table of word counts
    t = ST()  # new symbol table
    N = 0
    with open(filename, 'r') as f:
        # for line in f:
        for line in tqdm(f, total=get_num_lines(filename)):
            # split the line on anything
            for word in pat.findall(line.lower()):
                N += 1  # count total words
                if len(word) >= minlen:
                    try:
                        t[word] += 1
                    except KeyError:
                        t[word] = 1

    # Find the key with the highest frequency
    max_word = ""
    max_freq = 0
    for word in t:
        if t[word] > max_freq:
            max_word = word
            max_freq = t[word]
    print(f"N = {N}")
    print(max_word, max_freq)

    return t


if __name__ == '__main__':
    # filename = 'data/tiny_tale.txt'   # 292
    filename = 'data/tale.txt'          # 779K
    # filename = 'data/leipzig1m.txt'     # 124M

    minlen = 8

    ST = SequentialSearchST
    # ST = BinarySearchST

    t = frequency_counter(ST, filename, minlen=minlen)
    # pickle.dump(t, open(f"tale_{ST.__name__}_N{minlen}.pkl", 'wb'))

# =============================================================================
# =============================================================================
