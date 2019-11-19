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

import re

from tqdm import tqdm


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
        for i, line in enumerate(fp, 1):
            pass
        fp.seek(0)  # rewind file
        return i

    def count_frequencies(self, filename, minlen=1):
        """Build symbol table of word counts, and find the max."""
        # Compute the frequency counts
        with open(filename, 'r') as fp:
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


# =============================================================================
# =============================================================================
