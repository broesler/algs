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

from algs.basics import Bag
from algs.search import HashST, MultiValHashST, invert

# TODO add `header=True` to parse header line


class LookupCSV():
    """A symbol table dicionary client for reading CSV files."""

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
        if multival:
            self.st = MultiValHashST()
        else:
            self.st = HashST()
        if header is None:
            header = 0
        # Build the dictionary from the file
        with open(Path(filename), 'r') as fp:
            for line in fp.readlines()[header:]:
                items = line.strip().split(delim)
                k, v = items[key_col], items[val_col]
                self.st[k] = v

    def query(self, k):
        """Return the value associated with `k`."""
        if k in self.st:
            return self.st[k]


class LookupIndex():
    """A symbol table indexing client for reading CSV files."""

    def __init__(self, filename, delim=',', header=None):
        """
        Parameters
        ----------
        filename : str
            The name of the delimited text file to read.
        delim : str, optional
            String on which to separate the input lines.
        header : int, optional
            Initial lines to skip when reading the file.
        """
        self.st = HashST()
        self.ts = HashST()
        if header is None:
            header = 0
        # Build the dictionary from the file
        with open(Path(filename), 'r') as fp:
            for line in fp.readlines()[header:]:
                items = line.strip().split(delim)
                k = items[0]
                for v in items[1:]:
                    if k not in self.st: self.st[k] = Bag()
                    if v not in self.ts: self.ts[v] = Bag()
                    self.st[k].add(v)
                    self.ts[v].add(k)

    def query(self, k):
        """Return the value associated with `k`."""
        if k in self.st:
            return self.st[k]
        if k in self.ts:
            return self.ts[k]

    def print_query(self, k):
        v = self.query(k)
        print(str(k) + '\n  ' + '\n  '.join(v))


# Exercise 3.5.22
class FullLookupCSV():
    """A symbol table dicionary client for reading CSV files."""

    # TODO What about duplicate values in a column? e.g. I want to know all
    # dates on which the DJIA Volume was a given number, or within a range.
    def __init__(self, filename, delim=',', header=None):
        """
        Parameters
        ----------
        filename : str
            The name of the delimited text file to read.
        delim : str, optional
            String on which to separate the input lines.
        header : int, optional
            Initial lines to skip when reading the file.
        """
        if header is None:
            header = 0
        # Build the dictionary from the file
        with open(Path(filename), 'r') as fp:
            # Build list of symbol tables
            lines = fp.readlines()
            items = lines[header].strip().split(delim)
            self.sts = len(items)*[None]

            for line in lines[header:]:
                items = line.strip().split(delim)
                for i, k in enumerate(items):
                    if self.sts[i] is None:
                        self.sts[i] = HashST()
                    # TODO use header for column names instead of numbers
                    # Each value is itself a symbol table for the value-index
                    # self.sts[i][k] = HashST([(j, v) for j, v in enumerate(items)])
                    self.sts[i][k] = list(items)

    def query(self, k, key_col, val_col=None):
        """Return the value associated with `k`.

        Parameters
        ----------
        k : str
            The key for which to search.
        key_col : int
            The 0-indexed column number to use for the keys.
        val_col : int, optional
            The 0-indexed column number to use for the values.
        """
        st = self.sts[key_col]
        if k in st:
            if val_col is None:
                return st[k]
            else:
                return st[k][val_col]


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

    print(f"---{filename} - indexed ---")
    st = LookupIndex(filename)
    st.print_query('Serine')
    st.print_query('TCC')

    filename = Path('../data/movies-top-grossing.txt')
    print(f"---{filename} - indexed ---")
    st = LookupIndex(filename, delim='/')
    st.print_query('Bacon, Kevin')
    st.print_query('Top Gun (1986)')

    # assert st.st == invert(st.ts)
    # assert st.ts == invert(st.st)

    filename = Path('../data/DJIA.csv')
    print(f"---{filename}---")
    st = FullLookupCSV(filename)
    q = '29-Oct-29'
    print(f"{q}: {st.query(q, key_col=0)}")
    print(f"{q}: {st.query(q, key_col=0, val_col=3)}")


# =============================================================================
# =============================================================================
