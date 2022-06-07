#!/usr/bin/env python3
# =============================================================================
#     File: concordance.py
#  Created: 2022-06-07 11:10
#   Author: Bernie Roesler
#
"""
Create a concordance of a text using a symbol table.
"""
# =============================================================================

import re

from pathlib import Path
from tqdm import tqdm

from util import count_lines
from algs.search import MultiST, RedBlackBST


class Concordance():
    """Class to index words and their locations in a text.

    Attributes
    ----------
    st : symbol table
        The symbol table where keys are words, and values are frequency counts.
    """

    # split on non-alphabet chars and underscores
    pat = re.compile(r"[a-zA-Z']+")
    offset = 3

    class _Node():
        """Data class to store the locations of words in the concordance."""
        def __init__(self, i, j, context=None):
            self.i = int(i)
            self.j = int(j)
            self.context = context

        def __str__(self):
            return (f"({self.i}, {self.j}): {self.context}\n")

        def __repr__(self):
            return f"<{self.__class__.__name__}>: {self.__str__()}"

    def __init__(self, filename, minlen=1, verbose=False):
        """
        Parameters
        ----------
        filename : str or Path
            The file from which to build the concordance.
        minlen : int >= 0, optional
            The minimum length of words to consider in the concordance.
        verbose : bool, optional
            If True, print a progress bar as the concordance is built.
        """
        self.st = MultiST()
        self.verbose = bool(verbose)
        with open(filename, 'r') as fp:
            iters = enumerate(fp)
            if self.verbose:
                iters = tqdm(iters, total=count_lines(fp))
            for i, line in iters:
                words = self.pat.findall(line.lower())
                for j, word in enumerate(words):
                    if len(word) >= minlen:
                        lo = max([0, j - self.offset])
                        hi = min([j + self.offset, len(line)])
                        # Add a node to the multi-valued index
                        context = ' '.join(words[lo:hi+1])
                        self.st[word] = self._Node(i, j, context)

    def query(self, k):
        """Return the information associated with the given word `k`."""
        return self.st.get_all(k)


class InvertedConcordance():
    """Invert a concordance by placing words at their line and index
    locations."""

    def __init__(self, c):
        self.lines = RedBlackBST()  # ordered index of line numbers
        for k, vals in c.st.items():
            for v in vals:
                if v.i not in self.lines:
                    self.lines[v.i] = RedBlackBST()
                self.lines[v.i][v.j] = k

    def concat(self):
        """Concatenate the words in each line, then all of the lines."""
        return '\n'.join([' '.join(x.values()) for x in self.lines.values()])


if __name__ == "__main__":
    import pydoc

    file = Path('../data/tiny_tale.txt')
    # file = Path('../data/tale.txt')

    c = Concordance(file, verbose=True)
    q = 'times'
    print(f"----- {repr(q)}? -----")
    print(c.query(q))

    print('----- Inverted -----')
    t = InvertedConcordance(c)
    # print(t.concat())
    pydoc.pager(t.concat())

# =============================================================================
# =============================================================================
