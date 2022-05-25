#!/usr/bin/env python3
# =============================================================================
#     File: unionfind.py
#  Created: 2022-05-25 14:58
#   Author: Bernie Roesler
#
"""
Description: Implementations of the Union-Find algorithms in §1.5.
"""
# =============================================================================

import re

from abc import ABC, abstractmethod
from pathlib import Path


class UF(ABC):
    # An abstract base class for the Union Find algorithms.
    _attribs_doc = """
    Attributes
    ----------
    count : int
        Number of components.
    """

    __doc__ = _attribs_doc

    def __init__(self, N, items=None, verbose=False):
        """Initialize `N` sites with integer names (0 to `N`-1).

        Parameters
        ----------
        N : int
            Number of sites.
        items : iterable of (int, int) tuples, optional
            List of connections to make.
        verbose : bool, optional
            If True, print unique pairs
        """
        self.N = N
        self.id = list(range(N))
        items = [] or items
        try:
            for p, q in items:
                if self.connected(p, q):
                    continue
                self.union(p, q)
                if verbose:
                    print(f"{p} {q}")
            if verbose:
                print(f"{self.count} components")
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             "expects an iterable mapping input.")

    @classmethod
    def fromfile(cls, filename, verbose=False):
        pat = re.compile(r"(\d+)\s+(\d+)")
        with open(Path(filename), 'r') as fp:
            N = int(fp.readline().strip())
            items = list()
            for line in fp.readlines():
                p, q = pat.findall(line.strip())[0]
                items.append((int(p), int(q)))
            return cls(N, items, verbose)

    @property
    def count(self):
        return self.N

    @abstractmethod
    def union(self, p, q):
        """Add a connection between sites `p` and `q`.

        Parameters
        ----------
        p, q : int
            Names of components to connect.
        """
        pass

    @abstractmethod
    def find(self, p):
        """Component identifier for site `p`. 
        
        .. note:: Returns the same integer for every site in each connected
        component. `union` must maintain this invariant.

        Parameters
        ----------
        p : int ∈ [0, N-1]
            Component identifier.

        Returns
        -------
        q : int ∈ [0, N-1]
            The component to which node `p` belongs.
        """
        pass

    def connected(self, p, q):
        """Component identifier for site `p`.

        Parameters
        ----------
        p, q : int ∈ [0, N-1]
            Component identifiers.

        Returns
        -------
        result : bool
            True if `p` and `q` are in the same component.
        """
        return self.find(p) == self.find(q)


class QuickFindUF(UF):
    __doc__ = f"""Implements a UnionFind with the quick-find algorithm.
               {UF.__doc__}"""

    def find(self, p):
        # The internal array `id` represents the name of the component to which
        # the node is connected, so `find` is just a quick lookup.
        return self.id[p]

    def union(self, p, q):
        # Put p and q into the same component
        pid = self.find(p)
        qid = self.find(q)

        # Nothing to do if they're already connected
        if pid == qid:
            return

        # Rename p's component to q's name
        for i in range(len(self.id)):
            if self.id[i] == pid:
                self.id[i] = qid
        self.N -= 1


if __name__ == "__main__":
    filename = './data/tinyUF.txt'
    uf = QuickFindUF.fromfile(filename, verbose=True)

# =============================================================================
# =============================================================================
