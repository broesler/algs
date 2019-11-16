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


class FrequencyCounter():
    """Class to count the frequencies of word occurrences in a given input.

    Parameters
    ----------
    ST : symbol table class
        The class of symbol table that will be used to store the frequencies.
    **kwargs : dict-like
        Any additional parameters will be passed to `ST`.

    Returns
    -------
    result : (M, N) ndarray
        Matrix of M vectors in K dimensions
    """
    # split on non-alphabet chars and underscores
    pat = re.compile(r"[a-zA-Z']+")

    def __init__(self, ST, **kwargs):
        self.t = ST(**kwargs)
        self.N = 0              # number of words in the input
        self.max_word = ''
        self.cost = list()  # count compares for each `put` operation

    @staticmethod
    def count_lines(fp):
        """Scan through file to count the number of lines."""
        # NOTE only works with fp = open(filename, 'r+') permissions
        buf = mmap.mmap(fp.fileno(), 0)
        lines = 0
        while buf.readline():
            lines += 1
        return lines

    def count_frequencies(self, fp, minlen=1):
        """Build symbol table of word counts."""
        self.N = 0
        for line in tqdm(fp, total=self.count_lines(fp)):
            for word in self.pat.findall(line.lower()):
                if len(word) >= minlen:
                    self.N += 1  # count all words matching criterion
                    try:
                        self.t[word] += 1
                    except KeyError:
                        self.t[word] = 1
                    # Track cost for each `put` operation, len(cost) == N
                    self.cost.append(self.t._cost)

        # Find the key with the highest frequency
        max_word = ''
        self.t[max_word] = 0
        for word in self.t:
            if self.t[word] > self.t[max_word]:
                max_word = word
        del self.t['']  # remove placeholder
        self.max_word = max_word  # store the result


if __name__ == '__main__':
    # Choose symbol table to test
    ST = SequentialSearchST
    # ST = BinarySearchST

    filenames = ['data/tiny_tale.txt',  # 292
                 'data/tale.txt']       # 779K
                 # 'data/leipzig1m.txt']  # 124M

    tags = [os.path.splitext(os.path.basename(x))[0] for x in filenames]
    df = pd.DataFrame(columns=pd.MultiIndex.from_product([tags, ['words', 'distinct', 'max_word', 'max_freq']]))

    for i, f in enumerate(filenames):
        tag = tags[i]
        for minlen in [1, 8, 10]:
            fc = FrequencyCounter(ST)
            fc.count_frequencies(open(f, 'r+'), minlen)
            df.loc[minlen, (tag, 'words')] = fc.N
            df.loc[minlen, (tag, 'distinct')] = fc.t.size
            df.loc[minlen, (tag, 'max_word')] = fc.max_word
            df.loc[minlen, (tag, 'max_freq')] = fc.t[fc.max_word]
            pickle.dump(fc, open(f"{tag}_{ST.__name__}_m{minlen:02d}.pkl", 'wb'))

    print(df)

# =============================================================================
# =============================================================================
