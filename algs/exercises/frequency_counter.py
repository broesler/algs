#!/usr/bin/env python3
# =============================================================================
#     File: frequency_counter.py
#  Created: 2019-11-06 21:53
#   Author: Bernie Roesler
#
"""
  Description: Create FrequencyCounter driver to test search classes.
"""
# =============================================================================

import re
import time

from tqdm import tqdm

from util import count_lines


class FrequencyCounter():
    """Class to count the frequencies of word occurrences in a given input.

    Parameters
    ----------
    ST : symbol table class
        The class of symbol table that will be used to store the frequencies.
    **kwargs : dict-like
        Any additional parameters will be passed to `ST`.

    Attributes
    ----------
    t : symbol table
        The symbol table where keys are words, and values are frequency counts.
    N : int
        The total number of words seen in the input.
    max_word : str
        The word with the highest frequency count. `self.t[max_word]` gives the
        count.
    cost : list
        A cumulative list of the number of compares/array accesses per `put`
        operation in `t`.
    """
    # split on non-alphabet chars and underscores
    pat = re.compile(r"[a-zA-Z']+")

    def __init__(self, ST, **kwargs):
        self.t = ST(**kwargs)
        self.N = 0              # number of words in the input
        self.max_word = ''
        self.cost = list()  # count compares for each `put` operation
        self.time = list()  # track actual timing of each `put` operation

    def count_frequencies(self, filename, minlen=1):
        """Build symbol table of word counts, and find the max."""
        # Compute the frequency counts
        with open(filename, 'r') as fp:
            for line in tqdm(fp, total=count_lines(fp)):
                for word in self.pat.findall(line.lower()):
                    if len(word) >= minlen:
                        self.N += 1  # count all words matching criterion
                        try:
                            tic = time.process_time()
                            self.t[word] += 1
                            toc = time.process_time()
                        except KeyError:
                            tic = time.process_time()
                            self.t[word] = 1
                            toc = time.process_time()
                        # Track cost for each `put` operation, len(cost) == N
                        self.cost.append(self.t._cost)
                        self.time.append(toc - tic)

    def find_max_word(self):
        """Find the key with the highest frequency."""
        max_word = ''
        self.t[max_word] = 0
        for word in self.t:
            if self.t[word] > self.t[max_word]:
                max_word = word
        del self.t['']  # remove placeholder
        self.max_word = max_word  # store the result
        return max_word


# =============================================================================
# =============================================================================
