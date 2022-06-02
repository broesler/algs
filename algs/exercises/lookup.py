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

from algs import Queue, HashST, MultiValHashST


class LookupCSV():
    """A symbol table dicionary client for reading CSV files."""

    # TODO add `header=True` to read header line
    def __init__(self, filename, key_col=0, val_col=1, delim=',', header=None,
                 multival=False):
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
        header : int, optional
            Initial lines to skip when reading the file.
        multival : bool, optional
            If True, store every value associated with the keys.
        """
        self.st = HashST()
        if header is None:
            header = 0
        # Build the dictionary from the file
        with open(Path(filename), 'r') as fp:
            for line in fp.readlines()[header:]:
                items = line.strip().split(delim)
                k, v = items[key_col], items[val_col]
                if multival:
                    if k not in self.st:
                        self.st[k] = Queue()
                    self.st[k].enqueue(v)
                else:
                    self.st[k] = v

    def query(self, k):
        """Return the value associated with `k`."""
        if k in self.st:
            return self.st[k]


if __name__ == "__main__":
    filename = Path('../data/airports.csv')
    print(f"---{filename}---")
    st = LookupCSV(filename, header=1)
    qs = ['EWR', 'BOS', 'MHT']
    for q in qs:
        print(f"{q}: {st.query(q)}")

    filename = Path('../data/amino.csv')
    print(f"---{filename}---")
    st = LookupCSV(filename, key_col=0, val_col=3)
    q = 'TCC'
    print(f"{q}: {st.query(q)}")

    print(f"---{filename} - multi-valued ---")
    st = LookupCSV(filename, key_col=3, val_col=0, multival=True)
    q = 'Serine'
    print(f"{q}: {st.query(q)}")

# =============================================================================
# =============================================================================
