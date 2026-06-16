#!/usr/bin/env python3
# =============================================================================
#     File: search.py
#  Created: 2026-06-12 11:58
#   Author: Bernie Roesler
# =============================================================================

"""Graph search algorithms."""

from abc import ABC, abstractmethod

from algs.basics import Queue, Stack


def _reconstruct_path(v, s, edge_to):
    """Reconstruct the list of vertices on the path from `v` to `s` using the
    `edge_to` array.
    """
    sources = {s} if isinstance(s, int) else set(s)
    path = Stack()
    x = v

    while x not in sources:
        path.push(x)
        x = edge_to[x]

        if x is None:
            return None  # no path exists

    path.push(x)
    return path


class GraphSearch(ABC):
    _DOC_TEMPLATE = """{descr}

    Parameters
    ----------
    G : :obj:`Graph`
        The graph over which to search.
    source : int or iterable of int, optional
        The index or indices of the source vertices.
    """

    __doc__ = _DOC_TEMPLATE.format(
        descr="""An abstract base class for implementing graph search algorithms.

        This class should not be instantiated, because it does not actually do
        anything. A subclass should call `super().__init__(G, s)` to initialize
        the search structure, and then implement the search itself, which
        should populate the `_marked` and `_edge_to` attributes. The
        `has_path_to` and `path_to` methods will then work as expected."""
    )

    @abstractmethod
    def __init__(self, G, source=None):
        if source is None:
            self._sources = list(G.vertices())
        if isinstance(source, (int, str)):
            self._sources = [source]
        else:
            self._sources = list(source)

        if hasattr(G._adj, "keys"):  # dict-based graph
            self._marked = dict.fromkeys(G.vertices(), False)
            self._edge_to = dict.fromkeys(G.vertices())
        else:
            self._marked = G.V * [False]
            self._edge_to = G.V * [None]  # last vertex on known path to this one

    @property
    def sources(self):
        """The source vertex or vertices from which the search was performed."""
        return self._sources

    @property
    def count(self):
        """The number of vertices connected to `s`."""
        if isinstance(self._marked, dict):
            return sum(self._marked.values())
        return sum(self._marked)

    def has_path_to(self, v):
        """Return True if there is a path from `s` to `v`."""
        return self._marked[v]

    def path_to(self, v):
        """Return an iterable of the vertices on the path from `s` to `v`."""
        if not self.has_path_to(v):
            return None

        return _reconstruct_path(v, self._sources, self._edge_to)


# -----------------------------------------------------------------------------
#         Paths/Searches
# -----------------------------------------------------------------------------
# See: Algorithm 4.1 DepthFirstPaths (p 536) + DepthFirstSearch (p 531)
class DepthFirstSearch(GraphSearch):
    __doc__ = GraphSearch._DOC_TEMPLATE.format(
        descr="Depth-first search to return a path."
    )

    def __init__(self, G, s):
        super().__init__(G, s)
        self._leaf = None  # Exercise 4.1.10
        for v in self._sources:
            if not self._marked[v]:
                self._dfs(G, v)

    def _dfs(self, G, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True

        for w in G.adj(v):
            if not self._marked[w]:
                self._edge_to[w] = v
                self._dfs(G, w)

        if self._leaf is None:
            self._leaf = v  # last seen vertex

    # Exercise 4.1.10
    @property
    def leaf(self):
        """The last vertex found by the search."""
        return self._leaf


# Web Exercise 28
class DepthFirstSearch_nr(DepthFirstSearch):
    __doc__ = GraphSearch._DOC_TEMPLATE.format(
        descr="""Non-recursive depth-first search.

        .. note:: Extra memory includes a list of iterators over each adjacency
        list, plus the stack of vertices. Explores vertices in the same order as
        recursive DFS."""
    )

    def _dfs(self, G, v):
        """Perform depth-first search from `v` with an explicit stack."""
        stack = Stack()
        adj = [iter(G.adj(v)) for v in G.vertices()]
        self._marked[v] = True
        stack.push(v)
        while not stack.is_empty:
            v = stack.peek()
            try:
                w = next(adj[v])
                if not self._marked[w]:
                    self._marked[w] = True
                    self._edge_to[w] = v
                    stack.push(w)
            except StopIteration:
                leaf = stack.pop()
                if self._leaf is None:
                    self._leaf = leaf  # last seen vertex


# Web Exercise 28
class DepthFirstSearch_nr_simple(DepthFirstSearch):
    __doc__ = GraphSearch._DOC_TEMPLATE.format(
        descr="""Non-recursive depth-first search.

        .. note:: Extra memory is proportional to V + E, since each vertex may be
        pushed more than once. This implementation explores adjacent vertices in
        the opposite order of recursive DFS."""
    )

    def _dfs(self, G, v):
        """Perform depth-first search from `v` with an explicit stack."""
        stack = Stack()
        stack.push(v)
        while not stack.is_empty:
            v = stack.pop()
            if not self._marked[v]:
                self._marked[v] = True
                for w in G.adj(v):
                    if not self._marked[w]:
                        self._edge_to[w] = v
                        stack.push(w)


# Algorithm 4.2
class BreadthFirstSearch(GraphSearch):
    __doc__ = GraphSearch._DOC_TEMPLATE.format(
        descr="Breadth-first search to find shortest paths."
    )

    def __init__(self, G, s):
        super().__init__(G, s)
        self._dist_to = G.V * [None]  # Exercise 4.1.13
        self._bfs(G)

    def _bfs(self, G):
        """Perform breadth-first search from vertex `v`."""
        q = Queue()

        for s in self._sources:
            self._marked[s] = True
            self._dist_to[s] = 0
            q.enqueue(s)

        while not q.is_empty:
            v = q.dequeue()
            for w in G.adj(v):
                if not self._marked[w]:
                    self._edge_to[w] = v
                    self._marked[w] = True
                    self._dist_to[w] = self._dist_to[v] + 1
                    q.enqueue(w)

    # Exercise 4.1.13
    def dist_to(self, v):
        """Return the distance from source to `v`. None if not connected."""
        return self._dist_to[v]


# See:
# <https://stackoverflow.com/questions/24476027/shortest-path-in-a-complement-graph-algorithm>
class ComplementBFS(GraphSearch):
    __doc__ = GraphSearch._DOC_TEMPLATE.format(
        descr="""Breadth-first search to find shortest paths in the
        complement graph."""
    )

    def __init__(self, G, s):
        super().__init__(G, s)
        self._dist_to = G.V * [None]  # Exercise 4.1.13
        self._bfs(G, s)

    def _bfs(self, G, v):
        """Perform breadth-first search from vertex `v`."""
        q = Queue()
        self._marked[v] = True
        self._dist_to[v] = 0
        q.enqueue(v)
        # NOTE should use a multi-set for fast deletion
        # L1 == all nodes *not* adjacent to v in G (i.e. *adjacent* in G')
        L1 = list(range(G.V))
        L1.remove(v)
        # L2 == all unmarked nodes *adjacent* to v in G
        L2 = []
        while not q.is_empty:
            v = q.dequeue()
            for w in G.adj(v):
                if not self._marked[w]:
                    L1.remove(w)
                    L2.append(w)
            for w in L1:
                self._edge_to[w] = v
                self._marked[w] = True
                self._dist_to[w] = self._dist_to[v] + 1
                q.enqueue(w)
            L1 = L2
            L2 = []

    # Exercise 4.1.13
    def dist_to(self, v):
        """Return the distance from source to `v`. None if not connected."""
        return self._dist_to[v]


# =============================================================================
# =============================================================================
