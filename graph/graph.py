#!/usr/bin/env python3
#==============================================================================
#     File: graph.py
#  Created: 2019-02-20 22:40
#   Author: Bernie Roesler
#
"""
  Description: Un/Directed Graphs and supporting classes
"""
#==============================================================================

class Digraph():
    """Directed graph represented as a dictionary of vertices.

    Parameters
    ----------
    vertices : iterable of vertex ids
        Iterable of vertices to initialize the directed `Digraph`.

        *NOTE*: Vertices are stored as a dictionary, so duplicate ids in the
        list will overwrite.

    Attributes
    ----------
    V : int
        Number of vertices in the graph.
    E : int
        Number of edges in the graph.
    adj : dict of lists of vertices
        `adj[v]` returns adjacency list of vertices to which `v` points.
    indegree : dict of int
        `indegree[v]` is number of vertices that have edges to `v`.
    """
    def __init__(self, vertices=list()):
        self.E = 0
        self.V = 0
        self.adj = dict()       # vertex adjacency list
        self.indegree = dict()  # list of vertex indegrees
        for v in vertices:
            self._init_vertex(v)

    def roots(self):
        """List of vertices with indegree zero."""
        return [v for v in self if self.indegree[v] == 0]

    def vertices(self):
        return self.adj.keys()

    def add_edge(self, a, b):
        """Add edge between two vertex ids.

        Parameters
        ----------
        a : str or int
            Starting vertex id
        b : str or int
            Ending vertex id
        """
        self.E += 1

        if a in self.adj:
            self.adj[a].append(b)
        else:
            self._init_vertex(a, [b])

        if b not in self.indegree:
            self._init_vertex(b)
        self.indegree[b] += 1

    def _init_vertex(self, v, w=list()):
        """Add a new vertex to the graph.

        Parameters
        ----------
        v : vertex id (str or int)
            Name of vertex to add to the graph
        w : list of vertex ids
            Adjacent vertices to `v`. May be empty.
        """
        self.V += 1
        self.adj[v] = list(w)
        self.indegree[v] = 0

    def __getitem__(self, v):
        return self.adj[v]

    def __iter__(self):
        yield from self.vertices()

    def __repr__(self):
        return str(self.adj).replace('],', ']\n')

    def __str__(self):
        return self.__repr__()

#==============================================================================
#==============================================================================
