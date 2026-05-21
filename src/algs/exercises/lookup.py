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
from tqdm import tqdm

from algs.basics import Bag
from algs.search import ST, MultiST, HashST, MultiHashST, invert

# TODO 
# * add `header=True` to parse header line
# * pass data types to use instead of strings


class LookupCSV():
    """A symbol table dicionary client for reading CSV files."""

    def __init__(self, filename, key_col=0, val_col=1, delim=',', header=None,
                 multival=False, verbose=True):
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
            self.st = MultiST()
        else:
            self.st = ST()
        if header is None:
            header = 0
        # Build the dictionary from the file
        with open(Path(filename), 'r') as fp:
            iters = fp.readlines()[header:]
        if verbose:
            iters = tqdm(iters)
        for line in iters:
            items = line.strip().split(delim)
            k, v = items[key_col], items[val_col]
            self.st[k] = v

    def query(self, k):
        """Return the value associated with `k`."""
        if k in self.st:
            return self.st[k]

    def query_range(self, lo, hi=None):
        """Return all of the values between `lo` and `hi`."""
        return self.st.values(lo, hi)


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

    def __init__(self, filename, delim=',', header=0, verbose=False):
        """
        Parameters
        ----------
        filename : str
            The name of the delimited text file to read.
        delim : str, optional
            String on which to separate the input lines.
        header : int, optional
            Line to use as column names.
        """
        self._col_names = None

        # Build the dictionary from the file
        with open(Path(filename), 'r') as fp:
            lines = fp.readlines()

        # Build list of symbol tables
        words = lines[header or 0].strip().split(delim)
        if header is None:
            self._col_names = range(len(words))
            self.sts = len(words)*[None]
        else:
            self._col_names = words
            self.sts = HashST.fromkeys(self._col_names)

        # Scan the file line-by-line
        iters = lines[header+1:]
        if verbose:
            iters = tqdm(iters)

        for line in iters:
            items = line.strip().split(delim)
            for col, k in zip(self._col_names, items):
                if self.sts[col] is None:
                    self.sts[col] = MultiHashST()

                # Each value is itself a symbol table for the value-index
                for c, v in zip(self._col_names, items):
                    if k not in self.sts[col]:
                        self.sts[col][k] = MultiHashST()
                    else:
                        self.sts[col][k][c] = v

    def query(self, k, key_col, val_col=None):
        """Return the value associated with `k`.

        Parameters
        ----------
        k : str
            The key for which to search.
        key_col : int or str
            The 0-indexed column number to use for the keys.
        val_col : int or str, optional
            The 0-indexed column number to use for the values.
        """
        st = self.sts[key_col]
        if k in st:
            if val_col is None:
                return st[k]
            else:
                return st[k].get_all(val_col)


if __name__ == "__main__":
    filename = Path('../data/airports.csv')
    print(f"---{filename}---")
    st = LookupCSV(filename, header=1)
    qs = ['EWR', 'BOS', 'MHT']
    for q in qs:
        print(f"{q}: {st.query(q)}")

    # Unique codons, multiple amino acids
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

    # Unique movie titles, multiple actor names
    filename = Path('../data/movies-top-grossing.txt')
    print(f"---{filename} - indexed ---")
    st = LookupIndex(filename, delim='/')
    st.print_query('Bacon, Kevin')
    st.print_query('Top Gun (1986)')

    # assert st.st == invert(st.ts)
    # assert st.ts == invert(st.st)

    # unique ranks and words with repeated frequencies and/or part of speech
    filename = Path('../data/bnc-wordfreq.csv')
    print(f"---{filename}---")
    st = FullLookupCSV(filename, verbose=True)
    q = 'about'
    print(f"{q}: {st.query(q, key_col='WORD')}")
    print(f"{q}: {st.query(q, key_col='WORD', val_col='RANK')}")
    print(f"{q}: {st.query(q, key_col='WORD', val_col='FREQUENCY')}")
    print(f"{q}: {st.query(q, key_col='WORD', val_col='PART OF SPEECH')}")
    q = 'prep'
    # print(f"{q}: {st.query(q, key_col='PART OF SPEECH')}")
    # Return all words that are prepositions
    print(f"{q}: {st.query(q, key_col='PART OF SPEECH', val_col='WORD')}")

    # unique dates with floats
    filename = Path('../data/DJIA.csv')
    print(f"---{filename}---")
    st = LookupCSV(filename, key_col=0, val_col=3, verbose=True)
    lo = '29-Oct-29'
    hi = '11-Nov-29'
    print(f"{lo, hi}: {st.query_range(lo, hi)}")

# =============================================================================
# =============================================================================
