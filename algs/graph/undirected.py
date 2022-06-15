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


class Graph(ABC):
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
                G.add_edge(v, w)
            return G

    @abstractmethod
    def add_edge(self, v, w):
        """Add an edge from `v` to `w`."""
        pass

    @abstractmethod
    def adj(self, v):
        """Return an iterable of vertices adjacent to `v`."""
        pass

# =============================================================================
# =============================================================================
