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
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms

from abc import ABC, abstractmethod
from pathlib import Path

from algs.basics import RandomBag


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
    N : int
        Number of sites.
    E : int
        Number of edges.
    edges : list of (int, int)
        If `store=True`, keeps list of `(p, q)` tuples of edges made.
    """

    __doc__ = _attribs_doc

    def __init__(self, N, items=None, store=False):
        """Initialize `N` sites with integer names (0 to `N`-1).

        Parameters
        ----------
        N : int
            Number of sites.
        items : iterable of (int, int) tuples, optional
            List of connections to make.
        store : bool, optional
            If True, keep a list `edges` of tuples `(p, q)`.
        """
        self.N = N
        self.count = N
        self.E = 0
        self.id = list(range(N))
        self._cost = 0   # cost of last operation
        self._total = 0  # total cost of all operations
        self.edges = []
        items = items or []
        try:
            for p, q in items:
                if not self.connected(p, q):
                    self.union(p, q)
                    self.E += 1
                    if store:
                        self.edges.append((p, q))
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             "expects an iterable mapping input.")

    @classmethod
    def fromfile(cls, filename, **kwargs):
        N, items = read_uf_file(filename)
        return cls(N, items, **kwargs)

    def _validate_edges(self):
        assert self.E == len(self.edges)

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
                and self.edges == other.edges)


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
        self._cost = 0
        # Follow links up to the root
        r = p
        while r != self.id[r]:
            r = self.id[r]
            self._cost += 1
        # Exercise 1.5.12
        if self._COMPRESS_PATHS:
            while p != r:
                x = self.id[p]  # pointer to next node up
                self.id[p] = r  # change the parent of the leaf to the root
                p = x           # move the pointer up
                self._cost += 1
        return r

    def union(self, p, q):
        # Compare the roots of each node's tree component
        cost = 0
        p_root = self.find(p); cost += self._cost
        q_root = self.find(q); cost += self._cost

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


# Algorithm 1.5 (p 228)
class WeightedQuickUnionUF(QuickUnionUF):
    __doc__ = f"""Implements a weighted quick-union algorithm.

               Similar to quick-union, but tracks tree sizes for balance.
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


class HeightWeightedQuickUnionUF(WeightedQuickUnionUF):
    __doc__ = f"""Implements a weighted quick-union algorithm, but uses tree
               height for comparison instead of size.

               Performance is guaranteed logarithmic.
               {UF.__doc__}."""

    def __init__(self, N, *args, **kwargs):
        self.height = N*[0]
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

        # Make the shorter root point to the taller one
        if self.height[i] < self.height[j]:
            self.id[i] = j
            cost += 1
        elif self.height[i] > self.height[j]:
            self.id[j] = i
            cost += 1
        else:
            self.id[j] = i
            self.height[i] += 1
            cost += 2

        # Update counts
        self.count -= 1
        self._cost = cost
        self._total += cost


# Exercise 1.5.20
class DynamicWeightedQuickUnionUF(WeightedQuickUnionUF):
    __doc__ = f"""Implements a weighted quick-union algorithm with dynamic
               sizing of the sites.

               Performance is guaranteed logarithmic.
               {UF.__doc__}."""

    _MIN_SITES = 5

    def __init__(self, *args, **kwargs):
        N = self._MIN_SITES
        self.sz = N*[1]  # track tree sizes
        super().__init__(N, *args, **kwargs)

    def find(self, p):
        if p >= self.N:
            self._new_site(p)
        return super().find(p)

    def _new_site(self, p):
        """Add new sites to accomodate up to an index of `p`."""
        # Resize the `id` and `sz` arrays to add new site(s)
        _N = p+1
        # Resize id array
        _id = _N*[None]
        _id[:self.N] = self.id            # copy existing
        _id[self.N:] = range(self.N, _N)
        # Resize sz array
        _sz = _N*[1]
        _sz[:self.N] = self.sz
        # Copy to self
        self.id = _id
        self.sz = _sz
        self.count += _N - self.N
        self.N = _N

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


# Exercise 1.5.17
class ErdosRenyi():
    """Creates a random connected graph.

    Parameters
    ----------
    N : int
        Number of sites.
    UF : UnionFind class
        Class of union-find algorithm to compute the graph.

    Attributes
    -------
    uf : UnionFind class
        The provided `UF` class with completed connections.
    E : int
        The number of edges in the graph.
    """
    rng = np.random.default_rng()

    def __init__(self, N, UF=WeightedQuickUnionUF, store=False, **kwargs):
        self.N = N
        self.uf = UF(N, store=store, **kwargs)
        self.E = 0
        # Generate random pairs of sites until all are connected
        while self.uf.count > 1:
            p, q = self.rng.integers(self.N, size=2)
            if not self.uf.connected(p, q):
                self.uf.union(p, q)
                if store:
                    self.made_connections.append((p, q))
            self.E += 1


# Exercise 1.5.18
def full_grid(N):
    """Create a list of the connections in an `N`-by-`N` grid.

    Parameters
    ----------
    N : int
        Number of sites.

    Returns
    -------
    connections : list of (int, int)
        A list of every connection made in the graph.
    """
    items = list()
    for i in range(N):
        for j in range(i*N, (i+1)*N):
            # Connect across a row
            if j < (i+1)*N-1:
                items.append((j, j+1))
            # Connect to next column
            if i < N-1:
                items.append((j, j+N))
    return items


# Exercise 1.5.18
def random_grid(N):
    """Create a randomized list of the connections in an `N`-by-`N` grid.

    Parameters
    ----------
    N : int
        Number of sites.

    Returns
    -------
    connections : list of (int, int)
        A list of every connection made in the graph.
    """
    rng = np.random.default_rng()
    items = RandomBag()
    for i in range(N):
        for j in range(i*N, (i+1)*N):
            r, s = rng.random(2)  # randomly order the pairs
            # Connect across a row
            if j < (i+1)*N-1:
                if r > 0.5:
                    item = (j, j+1)
                else:
                    item = (j+1, j)
                items.add(item)
            # Connect to next column
            if i < N-1:
                if s > 0.5:
                    item = (j, j+N)
                else:
                    item = (j+N, j)
                items.add(item)
    return items


def plot_grid(N, g, label_nodes=False, fig=None, ax=None, **kwargs):
    """Plot an `N`-by-`N` grid of sites and their connections.

    Parameters
    ----------
    N : int
        Number of sites per side.
    g : list of (int, int)
        List of edges.
    label_nodes : bool
        If True, label the sites with integer indices.
    fig, ax : Figure and Axes
        The figure and axes in which to make the plot. If None, the current
        figure and axes will be used, respectively.

    Returns
    -------
    ax : Axes
        The axes in which the plot is drawn.
    """
    if fig is None:
        fig = plt.gcf()
    if ax is None:
        ax = plt.gca()

    y, x = np.mgrid[:N, :N]
    x, y = np.ravel(x), np.ravel(y)

    ax.scatter(x, y, c='k', s=10, zorder=2)

    # Plot the edges
    for p, q in g:
        ax.plot((x[p], x[q]), (y[p], y[q]), 'k-', **kwargs)

    if label_nodes:
        # Label the nodes
        trans_offset = mtransforms.offset_copy(ax.transData, fig=fig,
                                               x=-5, y=5, units='points')
        for i, (xn, yn) in enumerate(zip(x, y)):
            ax.text(xn, yn, f"{i}", ha='right', va='bottom',
                    transform=trans_offset)

    ax.set_aspect('equal')
    ax.invert_yaxis()  # top-down as drawn by hand
    # ax.grid('on')
    ax.axis('off')  # hide everything but the grid

    return ax


if __name__ == "__main__":
    # Test reading from a file
    filename = './data/tinyUF.txt'
    uf = QuickFindUF.fromfile(filename, store=True)
    for p, q in uf.edges:
        print(f"{p} {q}")
    print(f"{uf.count} components")

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

    qup = QuickUnionUF(N, items, compress_paths=True, store=True)
    assert qup.compare(qu)
    df = DynamicWeightedQuickUnionUF(items, compress_paths=False, store=True)
    assert df.compare(wf)

# =============================================================================
# =============================================================================
