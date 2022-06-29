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

from algs.basics import Stack, Queue
from algs.graph.undirected import UndirectedGraph, Graph, SymbolGraph, CC


# -----------------------------------------------------------------------------
#         Abstract Base Classes
# -----------------------------------------------------------------------------
class DirectedGraph(UndirectedGraph):
    # Extends the UndirectedGraph ABC.
    def reverse(self):
        """Return the reverse of this digraph."""
        R = self.__class__(self.V)
        for v in self.vertices():
            for w in self.adj(v):
                R.add_edge(w, v)
        return R


# -----------------------------------------------------------------------------
#         Graphs
# -----------------------------------------------------------------------------
class Digraph(DirectedGraph, Graph):
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


class SymbolDigraph(SymbolGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, kind=Digraph)


# -----------------------------------------------------------------------------
#         Paths/Searches
# -----------------------------------------------------------------------------
# Algorithm 4.4
class DirectedDFS:
    """Implements depth-first search in a digraph."""

    def __init__(self, G, sources):
        """
        Parameters
        ----------
        G : :obj:`Digraph`
            The graph over which to search.
        sources : int or iterable
            A single source index, or an iterable of indices from which to
            begin the search.
        """
        self._marked = G.V * [False]
        try:
            for s in sources:
                self._dfs(G, s)
        except TypeError:
            self._dfs(G, sources)

    def marked(self, v):
        """Return True if a vertex has been visited."""
        return self._marked[v]

    def _dfs(self, G, v):
        self._marked[v] = True
        for w in G.adj(v):
            if not self._marked[w]:
                self._dfs(G, w)


class DirectedCycle:
    """Implements depth-first search to find a directed cycle."""

    def __init__(self, G):
        self._marked = G.V * [False]
        self._edge_to = G.V * [None]
        self._on_stack = G.V * [False]
        self.cycle = None
        for v in G.vertices():
            if not self._marked[v]:
                self._dfs(G, v)

    @property
    def has_cycle(self):
        return bool(self.cycle)

    def _dfs(self, G, v):
        self._on_stack[v] = True
        self._marked[v] = True
        for w in G.adj(v):
            if self.has_cycle:
                return
            elif not self._marked[w]:
                self._edge_to[w] = v
                self._dfs(G, w)
            elif self._on_stack[w]:
                # Found a cycle
                self.cycle = Stack()
                x = v
                while x != w:
                    self.cycle.push(x)
                    x = self._edge_to[x]
                self.cycle.push(w)
                self.cycle.push(v)
        self._on_stack[v] = False


class DepthFirstOrder:
    """Compute the pre-, post-, and reverse post-order traversals of the
    digraph."""

    def __init__(self, G):
        self.pre = Queue()
        self.post = Queue()
        self.reverse_post = Stack()
        self._marked = G.V * [False]
        for v in G.vertices():
            if not self._marked[v]:
                self._dfs(G, v)

    def _dfs(self, G, v):
        self.pre.enqueue(v)
        self._marked[v] = True
        for w in G.adj(v):
            if not self._marked[w]:
                self._dfs(G, w)
        self.post.enqueue(v)
        self.reverse_post.push(v)


# Algorithm 4.5
class Topological:
    """Compute the topological ordering of a digraph."""

    def __init__(self, G):
        self.order = None
        # If the graph is a DAG, it has an order
        c = DirectedCycle(G)
        if not c.has_cycle:
            dfs = DepthFirstOrder(G)
            self.order = dfs.reverse_post

    @property
    def is_DAG(self):
        return self.order is not None


# Algorithm 4.6
class KosarajuSCC(CC):
    """Implements Kosaraju's algorithm for computing strong components."""

    def __init__(self, G):
        order = DepthFirstOrder(G.reverse())
        super().__init__(G, vertices=order.reverse_post)

    def strongly_connected(self, v, w):
        return self.connected(v, w)  # semantic distinction


class TransitiveClosure:
    """Computes the transitive closure of a digraph.

    .. note:: This algorithm uses O(V²) space and O(V(V+E)) time!
        Each DFS uses O(V) space, and takes O(V+E) time, and we repeat the
        search for each of the V vertices in G.
    """

    def __init__(self, G):
        self._all = G.V * [None]
        for v in G.vertices():
            self._all[v] = DirectedDFS(G, v)

    def reachable(self, v, w):
        """Return True if `w` is reachable from `v`."""
        return self._all[v].marked(w)


# -----------------------------------------------------------------------------
#         Graph Properties
# -----------------------------------------------------------------------------
class Degrees:
    """Compute the in- and outdegrees of each vertex."""

    def __init__(self, G):
        self._indegree = G.V * [0]
        self._outdegree = G.V * [0]
        for v in G.vertices():
            adj = G.adj(v)
            self._outdegree[v] = len(adj)
            for w in adj:
                self._indegree[w] += 1
        self._sources = [v for v in G.vertices() if self._indegree[v] == 0]
        self._sinks = [v for v in G.vertices() if self._outdegree[v] == 0]

    def indegree(self, v):
        """Return the number of edges pointing to `v`."""
        return self._indegree[v]

    def outdegree(self, v):
        """Return the number of edges pointing from `v`."""
        return self._outdegree[v]

    def sources(self):
        """Return a list of vertices with indegree 0."""
        return self._sources

    def sinks(self):
        """Return a list of vertices with outdegree 0."""
        return self._sinks

    @property
    def is_map(self):
        """Return True if `G` is a map from the set of integers [0, V-1] onto
        itself."""
        return G._SELF_LOOPS and all([x == 1 for x in self._outdegree])


# Exercise 4.2.8
def check_topological(G, order):
    """Return True if `order` is a topological order of `G`."""
    if not Topological(G).is_DAG:
        raise ValueError('G is not a DAG!')
    if sorted(order) != sorted(G.vertices()):
        raise ValueError("order is not a permutation of G's vertices!")
    # Check if each vertex in the given order has all of its adjacent vertices
    # *later* in the order.
    index = dict({v: i for i, v in enumerate(order)})
    for v in order:
        for w in G.adj(v):
            if index[w] < index[v]:
                return False
    return True
    

# -----------------------------------------------------------------------------
#         Tests
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    from random import shuffle
    from algs.graph.undirected import (DepthFirstPaths, BreadthFirstPaths,
                                       print_paths)

    print('----- Digraph -----')
    G = Digraph.fromfile('../data/tinyDG.txt')
    print(G)
    print('----- Reverse -----')
    R = G.reverse()
    print(R)

    print('----- DirectedDFS -----')
    dfs = DirectedDFS(G, 2)
    print(' '.join(f"{v} " for v in G.vertices() if dfs.marked(v)))
    dfs = DirectedDFS(G, [1, 2, 6])
    print(' '.join(f"{v} " for v in G.vertices() if dfs.marked(v)))

    print('----- DFS Paths -----')
    print_paths(G, 0, GS=DepthFirstPaths)
    print('----- BFS Paths -----')
    print_paths(G, 0, GS=BreadthFirstPaths)

    print('----- Cycle -----')
    c = DirectedCycle(G)
    assert c.has_cycle
    print(c.cycle)

    print('----- Orders -----')
    p = DepthFirstOrder(G)
    print(p.pre)
    print(p.post)
    print(p.reverse_post)
    assert list(reversed(list(p.post))) == list(p.reverse_post)

    t = Topological(G)
    assert not t.is_DAG

    sg = SymbolDigraph.fromfile('../data/jobs.txt', delim='/')
    t = Topological(sg.G)
    assert t.is_DAG
    print('\n'.join(sg.name(v) for v in t.order))

    cc = KosarajuSCC(G)
    assert cc.count() == 5
    print(cc.get_components())

    d = Degrees(G)
    assert d._indegree == [2, 1, 2, 2, 3, 2, 1, 1, 1, 3, 1, 1, 2]
    assert d._outdegree == [2, 0, 2, 2, 2, 1, 3, 2, 2, 2, 1, 2, 1]
    assert d.sources() == []
    assert d.sinks() == [1]

    G2 = Digraph.fromfile('../data/tinyDG2.txt')
    print(G2)
    d = Degrees(G2)
    assert d._indegree == [1, 2, 2, 2, 1, 0, 2, 0, 2, 0, 2, 2]
    assert d._outdegree == [1, 1, 2, 2, 1, 2, 1, 2, 2, 0, 1, 1]
    assert d.sources() == [5, 7, 9]
    assert d.sinks() == [9]

    print('----- DAGs -----')
    G = Digraph.fromfile('../data/tinyDAG.txt')
    print(G)
    orders = DepthFirstOrder(G)
    print('   pre:', orders.pre)
    print('  post:', orders.post)
    print('r_post:', orders.reverse_post)
    t = Topological(G)
    print('  topo:', t.order)
    assert t.order == orders.reverse_post

    assert check_topological(G, t.order)
    order = list(t.order)
    shuffle(order)
    assert not check_topological(G, order)

# =============================================================================
# =============================================================================
