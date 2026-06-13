#!/usr/bin/env python3
# =============================================================================
#     File: search.py
#  Created: 2026-06-12 11:58
#   Author: Bernie Roesler
# =============================================================================

"""Graph search algorithms."""

from abc import ABC, abstractmethod
from collections import deque

from algs.basics import Queue, Stack
from algs.unionfind import WeightedQuickUnionUF


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
    def __init__(self, G, source=0):
        if isinstance(source, int):
            self._sources = [source]
        else:
            self._sources = list(source)
        self._marked = G.V * [False]
        self._edge_to = G.V * [None]  # last vertex on known path to this one

    @property
    def sources(self):
        """The source vertex or vertices from which the search was performed."""
        return self._sources

    @property
    def count(self):
        """The number of vertices connected to `s`."""
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


class STDepthFirstPaths(DepthFirstSearch):
    __doc__ = GraphSearch._DOC_TEMPLATE.format(
        descr="Depth-first search to return a path in an STGraph."
    )

    def __init__(self, G, s):
        self.s = s
        self._marked = dict.fromkeys(G.vertices(), False)
        self._edge_to = dict.fromkeys(G.vertices())
        self.leaf = self._dfs(G, s)

    def _dfs(self, G, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        for w in G.adj(v):
            if not self._marked[w]:
                self._edge_to[w] = v
                return self._dfs(G, w)
        return v  # last seen vertex


# Web Exercise 28
class DepthFirstPaths_nr(DepthFirstSearch):
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
                stack.pop()


# Web Exercise 28
class DepthFirstPaths_nr_simple(DepthFirstSearch):
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


# Exercise 4.1.8
class UFSearch(GraphSearch):
    __doc__ = GraphSearch._DOC_TEMPLATE.format(
        descr="""Graph search API using Union-Find.

        .. note:: This implementation is simple and efficient if we are only
            concerned with determining connectivity. The UF algorithm is also an
            *online* algorithm, as opposed to DFS which must preprocess the entire
            graph structure."""
    )
    # See p 529

    def __init__(self, G, s):
        self.s = s
        self._uf = WeightedQuickUnionUF(G.V)
        for v in G.vertices():
            for w in G.adj(v):
                if not self._uf.connected(v, w):
                    self._uf.union(v, w)

    @property
    def count(self):
        """The number of vertices connected to `s`.

        .. note::
           This value is not the same as the size of the component, since `s`
           may not be connected to all vertices in the component.
        """
        # Return the size of the component to which the source belongs
        return self._uf._size[self._uf.find(self.s)]

    def has_path_to(self, v):
        """Return True if `v` is connected to `s`."""
        return self._uf.connected(self.s, v)

    def path_to(self, v):
        """Not implemented since UF does not keep track of paths."""
        raise NotImplementedError("UFSearch does not keep track of paths!")


# Exercise 4.1.10
class LeafDFS(GraphSearch):
    __doc__ = GraphSearch._DOC_TEMPLATE.format(
        descr="""Depth-first search to find a non-structural
        vertex, aka a leaf of a spanning tree rooted at the source."""
    )

    def __init__(self, G, s):
        super().__init__(G, s)
        self._leaf = self._dfs(G, s)

    @property
    def leaf(self):
        """The leaf vertex found by the search."""
        return self._leaf

    def _dfs(self, G, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        for w in G.adj(v):
            if not self._marked[w]:
                return self._dfs(G, w)
        return v  # return the leaf immediately when we find it


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


def _cycle_dfs(G, v, marked, edge_to, u=None, return_path=False):
    """Perform depth-first search recursively from vertex `v`.

    .. note:: `u` is the previously-seen vertex. If one of the adjacent
        vertices to `v` is marked, but is not the vertex from which we just
        came, we have a cycle.
    """
    if u is None:
        u = v  # set previous vertex to self for the first call

    marked[v] = True

    for w in G.adj(v):
        if not marked[w]:
            edge_to[w] = v
            result = _cycle_dfs(G, w, marked, edge_to, v, return_path)
            if result:
                return result
        elif w != u:
            if not return_path:
                return True  # cycle found, but don't need to return the path

            cycle = Stack()
            x = v
            while x != w:
                cycle.push(x)
                x = edge_to[x]
            cycle.push(w)
            cycle.push(v)
            return cycle

    return None  # no cycle found


def _cycle_dfs_nr(G, v, marked, edge_to, return_path=False):
    """Perform depth-first search non-recursively from vertex `v`.

    .. note:: `u` is the previously-seen vertex. If one of the adjacent
        vertices to `v` is marked, but is not the vertex from which we just
        came, we have a cycle.
    """
    stack = Stack()
    adj = [iter(G.adj(v)) for v in G.vertices()]
    marked[v] = True
    stack.push(v)

    while not stack.is_empty:
        v = stack.peek()
        u = edge_to[v]  # previous vertex
        try:
            w = next(adj[v])
            if not marked[w]:
                edge_to[w] = v
                u = v
                marked[w] = True
                stack.push(w)
            elif w != u:
                cycle = Stack()
                x = v
                while x != w:
                    cycle.push(x)
                    x = edge_to[x]
                cycle.push(w)
                cycle.push(v)
                return cycle
        except StopIteration:
            stack.pop()

    return None  # no cycle found


def has_cycle(G, s, recursive=False):
    """Return True if there is a cycle in the graph that contains `s`.

    .. note:: This function assumes that `G` has no self-loops or parallel
        edges, but does not check this condition.

    Parameters
    ----------
    G : :class:`Graph`
        The graph to analyze.
    s : int
        The source vertex from which to start the search.
    recursive : bool
        If True, use the recursive implementation. Otherwise, use the
        non-recursive implementation. Both implementations return the same
        cycle.

    Returns
    -------
    bool
        True if there is a cycle in the graph that contains `s`. False
        otherwise.
    """
    marked = G.V * [False]
    edge_to = G.V * [None]  # last vertex on known path to this one
    engine = _cycle_dfs if recursive else _cycle_dfs_nr
    return bool(engine(G, s, marked, edge_to, return_path=False))


def find_cycle_path(G, s, recursive=False):
    """Find a cycle in the graph that contains `s`, if one exists.

    Parameters
    ----------
    G : :class:`Graph`
        The graph to analyze.
    s : int
        The source vertex from which to start the search.
    recursive : bool
        If True, use the recursive implementation. Otherwise, use the
        non-recursive implementation. Both implementations return the same
        cycle.

    Returns
    -------
    list
        A list of the vertices on the cycle, in order. If there is no cycle,
        returns an empty list.
    """
    marked = G.V * [False]
    edge_to = G.V * [None]  # last vertex on known path to this one
    engine = _cycle_dfs if recursive else _cycle_dfs_nr
    cycle = engine(G, s, marked, edge_to, return_path=True)
    return list(cycle) if cycle else []


def find_min_cycle(G, s):
    """Find the minimum cycle in the graph that contains `s`, if one exists.

    Parameters
    ----------
    G : :class:`Graph`
        The graph to analyze.
    s : int
        The source vertex from which to start the search.

    Returns
    -------
    list
        A list of the vertices on the minimum cycle, in order. If there is no
        cycle, returns an empty list.
    """
    cycle_length = float('inf')

    marked = G.V * [False]
    edge_to = G.V * [None]
    dist_to = G.V * [None]

    cycle_head = None  # start vertex of the cycle
    cycle_tail = None  # end vertex of the cycle

    # Run BFS from `s`.
    q = Queue()
    marked[s] = True
    dist_to[s] = 0
    q.enqueue(s)

    while not q.is_empty:
        v = q.dequeue()
        for w in G.adj(v):
            # Skip backtracking edge to parent
            if w == edge_to[v]:
                continue

            if not marked[w]:
                edge_to[w] = v
                marked[w] = True
                dist_to[w] = dist_to[v] + 1
                q.enqueue(w)
            else:
                d = dist_to[v] + dist_to[w] + 1
                if d < cycle_length:
                    cycle_head = w
                    cycle_tail = v
                    cycle_length = d

    if cycle_length == float('inf'):
        return []  # no cycle found

    # BFS gives two paths: one each from the source to the head and tail.
    # Merge the paths to head and tail to remove all common ancestors
    # except the last that completes the cycle.
    p = deque(_reconstruct_path(cycle_tail, s, edge_to))
    q = deque(_reconstruct_path(cycle_head, s, edge_to))

    while len(p) > 2 and len(q) > 2 and p[0] == q[0] and p[1] == q[1]:
        p.popleft()
        q.popleft()

    p.popleft()  # remove one of the dulicates
    p.extendleft(q)  # merge
    p.append(p[0])  # complete the loop

    return list(p)


# =============================================================================
# =============================================================================
