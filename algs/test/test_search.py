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

import pandas as pd

from tqdm import tqdm

from algs.search import SequentialSearchST, BinarySearchST

pat = re.compile(r"[a-zA-Z']+")  # split on non-alphabet chars and underscores

def count_lines(filename):
    """Scan through file to count the number of lines."""
    fp = open(filename, 'r+')
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines


# TODO make into class to store more info... need to output list of
# ST._compares, where we append to the list after each `put` (`t[word]`)
def count_frequencies(ST, filename, minlen=1):
    # Build symbol table of word counts
    t = ST()  # new symbol table
    N = 0
    with open(filename, 'r') as f:
        for line in tqdm(f, total=count_lines(filename)):
            for word in pat.findall(line.lower()):
                if len(word) >= minlen:
                    N += 1  # count all words matching criterion
                    try:
                        t[word] += 1
                    except KeyError:
                        t[word] = 1

    # Find the key with the highest frequency
    max_word = ''
    t[max_word] = 0
    for word in t:
        if t[word] > t[max_word]:
            max_word = word
    del t['']  # remove placeholder
    return t, N, max_word


if __name__ == '__main__':
    # Choose symbol table to test
    ST = SequentialSearchST
    # ST = BinarySearchST

    filenames = ['data/tiny_tale.txt']  # 292
                 # 'data/tale.txt']       # 779K
                 # 'data/leipzig1m.txt']  # 124M

    # words = dict()
    tags = [os.path.splitext(os.path.basename(x))[0] for x in filenames]
    df = pd.DataFrame(columns=pd.MultiIndex.from_product([tags,
                                                             ['words', 'distinct', 'max_word', 'max_freq']]))
    for f in filenames:
        tag = os.path.splitext(os.path.basename(f))[0]  # i.e. 'tiny_tale'
        for minlen in [1, 8, 10]:
            t, N, max_word = count_frequencies(ST, f, minlen)
            df.loc[minlen, (tag, 'words')] = N
            df.loc[minlen, (tag, 'distinct')] = len(t)
            df.loc[minlen, (tag, 'max_word')] = max_word
            df.loc[minlen, (tag, 'max_freq')] = t[max_word]
            # print("words =", N)
            # print("distinct =", len(t))
            # print(max_word, t[max_word])

            # pickle.dump(t, open(f"{tag}_{ST.__name__}_m{minlen:02d}.pkl", 'wb'))

# =============================================================================
# =============================================================================
