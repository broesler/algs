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
import re

from tqdm import tqdm

from algs.search import SequentialSearchST, BinarySearchST

# filename = 'data/tiny_tale.txt'
filename = 'data/tale.txt'
ST = SequentialSearchST

regex = re.compile('[^a-z]')

def normalize(w):
    """Replace any non-alphabetic characters in a word."""
    word = regex.sub('', w.lower())
    return word

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
            for w in line.split():
                word = normalize(w)
                N += 1  # count total words
                if len(word) > minlen:
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
    print(max_word, max_freq)

    return t

# t = frequency_counter(SequentialSearchST, filename)
t = frequency_counter(BinarySearchST, filename)



# =============================================================================
# =============================================================================
