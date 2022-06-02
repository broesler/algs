#!/usr/bin/env python3
# =============================================================================
#     File: lookupcsv.py
#  Created: 2022-06-01 22:31
#   Author: Bernie Roesler
#
"""
A symbol table dicionary client for reading CSV files.
"""
# =============================================================================

from pathlib import Path

from algs import HashST


class LookupCSV():
    """A symbol table dicionary client for reading CSV files."""

    # TODO add `header=True` to read header line
    def __init__(self, filename, key_col=0, val_col=1, delim=','):
        """
        Parameters
        ----------
        filename : str
            The name of the delimited text file to read.
        key_col : int, optional
            The 0-indexed column number to use for the keys.
        val_col : int, optional
            The 0-indexed column number to use for the values.
        delim : str, optional
            String on which to separate the input lines.
        """
        self.st = HashST()
        # Build the dictionary from the file
        with open(Path(filename), 'r') as fp:
            for line in fp.readlines():
                items = line.strip().split(delim)
                self.st[items[key_col]] = items[val_col]

    def query(self, k):
        """Return the value associated with `k`."""
        if k in self.st:
            return self.st[k]


if __name__ == "__main__":
    filename = Path('../data/airports.csv')
    st = LookupCSV(filename)
    qs = ['EWR', 'BOS', 'MHT']
    for q in qs:
        print(f"{q}: {st.query(q)}")

# =============================================================================
# =============================================================================
