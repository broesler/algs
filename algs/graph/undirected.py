#!/usr/bin/env python3
# =============================================================================
#     File: undirected.py
#  Created: 2022-06-14 21:05
#   Author: Bernie Roesler
#
"""
Implementations of undirected graph representations and associated algorithms.

See Sedgewick and Wayne, §4.1.
"""
# =============================================================================

from abc import ABC, abstractmethod

from algs.basics import Bag


class AGraph(ABC):
    # An abstract base class implementing the Graph API. See p 522.
    """
    Attributes
    ----------
    V : int
        number of vertices
    E : int
        number of edges
    """

    def __init__(self, V=0):
        self.V = V
        self.E = 0

    @classmethod
    def fromfile(cls, filename):
        """Construct the graph structure from a file."""
        with open(filename, 'r') as fp:
            V = int(fp.readline())
            fp.readline()  # skip # of edges?
            G = cls(V)
            for line in fp.readlines():
                v, w = line.strip().split()
                G.add_edge(int(v), int(w))
            return G

    @abstractmethod
    def add_edge(self, v, w):
        """Add an edge from `v` to `w`."""
        pass

    @abstractmethod
    def adj(self, v):
        """Return an iterable of vertices adjacent to `v`."""
        pass

    def degree(self, v):
        """Return the degree of vertex `v`."""
        return len(self.adj(v))

    def __str__(self):
        s = f"{self.V} vertices, {self.E} edges\n"
        for v in range(self.V):
            s += f"{v}: " + ' '.join(str(w) for w in self.adj(v))
            if v < self.V-1:
                s += '\n'
        return s

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"


class Graph(AGraph):
    __doc__ = f"""Implements an undirected graph using adjacency lists.
        {AGraph.__doc__}"""

    def __init__(self, V):
        super().__init__(V)
        self._adj = [Bag() for _ in range(V)]

    def adj(self, v):
        return self._adj[v]

    def add_edge(self, v, w):
        self._adj[v].add(w)
        self._adj[w].add(v)
        self.E += 1


# Define some functions for use with graphs that would be too cumbersome to
# maintain in the basic API.
def max_degree(G, v):
    """Return the maximum degree all vertices in the graph."""
    m = 0
    for v in range(G.V):
        d = G.degree(v)
        if d > m:
            m = d
    return m


def avg_degree(G):
    """Compute the theoretical average degree of the graph."""
    return 2 * G.E / G.V


def self_loops(G):
    """Return the number of self-loops in the graph."""
    s = 0
    for v in range(G.V):
        for w in G.adj(v):
            if v == w:
                s += 1
    return s // 2  # each edge counted twice


if __name__ == "__main__":
    from pathlib import Path
    filename = Path('../data/tinyG.txt')
    G = Graph.fromfile(filename)
    print(G)

# =============================================================================
# =============================================================================
