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


def read_uf_file(filename):
    """Read a file with the standard union-find format.

    Parameters
    ----------
    filename : str
        Name of the file. May be a `Path` object.

    Returns
    -------
    N : int
        Number of sites.
    items : list of tuples of (int, int)
        Pairs of site IDs defining connections.
    """
    pat = re.compile(r"(\d+)\s+(\d+)")
    with open(Path(filename), 'r') as fp:
        N = int(fp.readline().strip())
        items = list()
        for line in fp.readlines():
            p, q = pat.findall(line.strip())[0]
            items.append((int(p), int(q)))
    return N, items


class UF(ABC):
    # An abstract base class for the Union Find algorithms. See p 219.
    _attribs_doc = """
    Attributes
    ----------
    count : int
        Number of components.
    """

    __doc__ = _attribs_doc

    def __init__(self, N, items=None, verbose=False, store=False):
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
        self.count = N
        self.id = list(range(N))
        self._cost = 0   # cost of last operation
        self._total = 0  # total cost of all operations
        if store:
            self._made_connections = list()
        items = items or []
        try:
            for p, q in items:
                if self.connected(p, q):
                    continue
                self.union(p, q)
                if store:
                    self._made_connections.append((p, q))
                if verbose:
                    print(f"{p} {q}")
            if verbose:
                print(f"{self.count} components")
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             "expects an iterable mapping input.")

    @classmethod
    def fromfile(cls, filename, **kwargs):
        N, items = read_uf_file(filename)
        return cls(N, items, **kwargs)

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
        cost = 0
        pid = self.find(p); cost += self._cost 
        qid = self.find(q); cost += self._cost
        self._cost = cost
        self._total += cost
        return pid == qid

    # NOTE this is a convenience for testing reference implementations. This
    # does not provide a robust comparison of graph structuers.
    # Would need to compare the components in each group. 
    def compare(self, other):
        """Comparison for like inputs."""
        return (self.count == other.count
                and self._made_connections == other._made_connections)


# Exercise 1.5.7 (see p 222)
class QuickFindUF(UF):
    __doc__ = f"""Implements a UnionFind with the quick-find algorithm.

                Performance is linear.
               {UF.__doc__}"""

    def find(self, p):
        # The internal array `id` represents the name of the component to which
        # the node is connected, so `find` is just a quick lookup.
        self._cost = 1
        return self.id[p]

    def union(self, p, q):
        # Put p and q into the same component
        cost = 0
        pid = self.find(p); cost += self._cost
        qid = self.find(q); cost += self._cost

        # Nothing to do if they're already connected
        if pid == qid:
            self._cost = cost
            self._total += cost
            return

        # Rename p's component to q's name
        for i in range(self.N):
            if self.id[i] == pid:
                self.id[i] = qid
                cost += 1
        cost += self.N

        # Update counts
        self.count -= 1
        self._cost = cost
        self._total += cost


# Exercise 1.5.7 (see p 224)
class QuickUnionUF(UF):
    __doc__ = f"""Implements a UnionFind with the quick-union algorithm.

               This class implements a parent-link representation of a forest
               of trees. Worst-case performance may be quadratic.
               {UF.__doc__}"""

    def __init__(self, *args, compress_paths=False, **kwargs):
        self._COMPRESS_PATHS = bool(compress_paths)  # Exercise 1.5.12
        super().__init__(*args, **kwargs)

    def find(self, p):
        # Follow links up to the root
        self._cost = 0
        while p != self.id[p]:
            p = self.id[p]
            self._cost += 1
        return p

    def compress_paths(self, p):
        # Follow links up to the root
        cost = 0
        r = self.find(p); cost += self._cost
        while p != self.id[p]:
            x = p           # keep a pointer to the previous leaf
            p = self.id[p]  # move the pointer up
            self.id[x] = r  # change the parent of the leaf to the root
            cost += 1
        self._cost = cost

    def union(self, p, q):
        # Compare the roots of each node's tree component
        cost = 0
        p_root = self.find(p); cost += self._cost
        q_root = self.find(q); cost += self._cost

        # Exercise 1.5.12
        if self._COMPRESS_PATHS:
            self.compress_paths(p); cost += self._cost
            self.compress_paths(q); cost += self._cost

        if p_root == q_root:
            self._cost = cost
            self._total += cost
            return
        # Add p to q's tree
        self.id[p_root] = q_root
        cost += 1
        # Update counts
        self.count -= 1
        self._cost = cost
        self._total += cost


# Exercise 1.5.11
class WeightedQuickFindUF(QuickFindUF):
    __doc__ = f"""Implements a weighted quick-find algorithm.

               Similar to quick-find, but tracks component sizes to merge the
               smaller component into the larger component.
               {UF.__doc__}."""

    def __init__(self, N, *args, **kwargs):
        self.sz = N*[1]  # track tree sizes
        super().__init__(N, *args, **kwargs)

    def union(self, p, q):
        # Put p and q into the same component
        cost = 0
        pid = self.find(p); cost += self._cost
        qid = self.find(q); cost += self._cost

        # Nothing to do if they're already connected
        if pid == qid:
            self._cost = cost
            self._total += cost
            return

        # Rename the smaller component to the larger
        if self.sz[pid] < self.sz[qid]:
            for i in range(self.N):
                if self.id[i] == pid:
                    self.id[i] = qid
                    cost += 1
            self.sz[qid] += self.sz[pid]
            cost += self.N + 1
        else:
            for i in range(self.N):
                if self.id[i] == qid:
                    self.id[i] = pid
                    cost += 1
            self.sz[pid] += self.sz[qid]
            cost += self.N + 1

        # Update counts
        self.count -= 1
        self._cost = cost
        self._total += cost


# Algorithm 1.5 (p 228)
class WeightedQuickUnionUF(QuickUnionUF):
    __doc__ = f"""Implements a weighted quick-union algorithm.

               Similar to quick-union, but tracks tree heights for balance.
               Performance is guaranteed logarithmic.
               {UF.__doc__}."""

    def __init__(self, N, *args, **kwargs):
        self.sz = N*[1]  # track tree sizes
        super().__init__(N, *args, **kwargs)

    def union(self, p, q):
        # Compare the roots of each node's tree component
        cost = 0
        i = self.find(p); cost += self._cost
        j = self.find(q); cost += self._cost

        # Nothing to do if they're already connected
        if i == j:
            self._cost = cost
            self._total += cost
            return

        # Make the smaller root point to the larger one
        if self.sz[i] < self.sz[j]:
            self.id[i] = j
            self.sz[j] += self.sz[i]
        else:
            self.id[j] = i
            self.sz[i] += self.sz[j]
        cost += 2

        # Update counts
        self.count -= 1
        self._cost = cost
        self._total += cost


if __name__ == "__main__":
    # Test reading from a file
    filename = './data/tinyUF.txt'
    uf = QuickFindUF.fromfile(filename, verbose=True)

    # Exercise 1.5.1, 1.5.2, 1.5.3, 1.5.11
    N = 10  # == 1 + max(max(items))  # number of sites
    items = [(9, 0),
             (3, 4),
             (5, 8),
             (7, 2),
             (2, 1),
             (5, 7),
             (0, 3),
             (4, 2)]

    qf = QuickFindUF(N, items, store=True)
    qu = QuickUnionUF(N, items, store=True)
    wq = WeightedQuickUnionUF(N, items, store=True)
    wf = WeightedQuickFindUF(N, items, store=True)
    assert qf.compare(qu)
    assert qu.compare(wq)
    assert wq.compare(wf)

    qup = QuickUnionUF(N, items, compress_paths=True)

# =============================================================================
# =============================================================================
