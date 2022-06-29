#!/usr/bin/env python3
# =============================================================================
#     File: directed.py
#  Created: 2022-06-28 21:49
#   Author: Bernie Roesler
#
"""
Implementations of undirected graph representations and associated algorithms.

See Sedgewick and Wayne, §4.2.
"""
# =============================================================================

from abc import abstractmethod

from algs.graph.undirected import UndirectedGraph, Graph


class DirectedGraph(UndirectedGraph):
    # Extends the UndirectedGraph ABC.
    def reverse(self):
        """Return the reverse of this digraph."""
        R = self.__class__(self.V)
        for v in self.vertices():
            for w in self.adj(v):
                R.add_edge(w, v)
        return R


class Digraph(Graph):
    __doc__ = f"""Implements a digraph using an array of adjacency lists.
    {UndirectedGraph.__doc__}"""

    def add_edge(self, v, w):
        self._validate_vertex(v)
        self._validate_vertex(w)
        # Exercise 4.2.5 no self-loops
        if not self._SELF_LOOPS and v == w:
            raise ValueError(f"{v} == {w}! No self-loops allowed.")
        if self._PARALLEL or not self.has_edge(v, w):
            self.E += 1
            self._adj[v].add(w)  # direction matters! Only change from Graph

    
if __name__ == "__main__":
    G = Digraph.fromfile('../data/tinyDG.txt')

# =============================================================================
# =============================================================================
