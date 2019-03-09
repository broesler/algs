#!/usr/bin/env python3
#==============================================================================
#     File: graph.py
#  Created: 2019-02-20 22:40
#   Author: Bernie Roesler
#
"""
  Description: Edge-weighted Directed Graphs and supporting classes
"""
#==============================================================================

import operator
from abc import ABC, abstractmethod
from .basics import Stack, Queue, PriorityQueue

INF = float('inf')
M_INF = float('-inf')

class DirectedEdge():
    """Implements a weighted directed edge from one vertex key to another.

    Parameters
    ----------
    a : key
        Starting vertex id
    b : key
        Ending vertex id
    weight : float, weight >= 0.0
        Positive weight of the edge
    """
    def __init__(self, v, w, weight=0.0):
        self.v = v
        self.w = w
        self.weight = weight

    def __repr__(self):
        return '<DirectedEdge: ' + self.__str__() + '>'

    def __str__(self):
        return f"{self.v}->{self.w} ({self.weight:3.2g})"


class Digraph():
    """Edge-weighted directed graph represented as a dictionary of vertices.

    Parameters
    ----------
    vertices : iterable of vertex ids
        Iterable of vertices to initialize the directed `Digraph`.

    .. note:: vertices are stored as a dictionary, so duplicate ids in the
        input will overwrite.

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
    outdegree : dict of int
        `outdegree[v]` is number of vertices that have edges from `v`.
    """
    def __init__(self, vertices=list()):
        self.E = 0
        self.V = 0
        self.adj = dict()       # vertex-keyed adjacency list of edges
        self.indegree = dict()  # list of vertex indegrees
        for v in vertices:
            self._init_vertex(v)

    def _init_vertex(self, v):
        """Add a new vertex to the graph.

        Parameters
        ----------
        v : key
            Name of vertex to add to the graph
        """
        if v not in self.adj:
            self.V += 1
        self.adj[v] = list()
        self.indegree[v] = 0

    @property
    def outdegree(self, v):
        return len(self.adj[v])

    def roots(self):
        """List of vertices with indegree zero."""
        return [v for v in self.adj if self.indegree[v] == 0]

    def edges(self):
        """Iterable of all the edges in the digraph."""
        the_edges = list()
        for v in self.adj:
            the_edges.extend(self.adj[v])
        return the_edges

    def vertices(self):
        """Iterable of all the vertex keys in the Digraph."""
        return self.adj.keys()

    def iter_adjs(self):
        """Iterators of the adjacent nodes to all vertices."""
        return {v: iter(self.adj[v]) for v in self.adj}

    def add_edge(self, a, b, w=0.0):
        """Add a weighted edge between two vertices.

        Parameters
        ----------
        a : key
            Starting vertex id.
        b : key
            Ending vertex id.
        w : float
            Weight of the edge.
        """
        self.E += 1

        edge = DirectedEdge(a, b, w)

        if a not in self.adj:
            self._init_vertex(a)
        self.adj[a].append(edge)

        if b not in self.indegree:
            self._init_vertex(b)
        self.indegree[b] += 1

    def reverse(self):
        """Return the reverse of the Digraph."""
        rev = Digraph()
        for v in self.adj:
            for edge in self.adj[v]:
                rev.add_edge(edge.w, v, edge.weight)
        return rev

    def __getitem__(self, v):
        return self.adj[v]

    def __iter__(self):
        yield from self.vertices()

    def __repr__(self):
        return '<Digraph: ' + self.__str__() + '>'

    def __str__(self):
        return str(self.adj)

#------------------------------------------------------------------------------
#        Graph Searches
#------------------------------------------------------------------------------
# TODO implement dist_to method for all searches
# TODO update __doc__ for GraphSearch -> subclasses to include common
# attributes in all documentation + custom subclass parameters/attributes
# TODO make _edge_to, _visited, _dist_to @property, @abstractmethod
class GraphSearch(ABC):
    """General graph search class.

    Parameters
    ----------
    G : :obj:`Digraph`
    sources : iterable of vertex ids, optional
        Iterable of vertex ids from which to begin the search.

    Attributes
    ----------
    G : :obj:`Digraph`
        The directed graph object to search.
    sources : iterable
        Iterable of given sources, or vertices with indegree 0.
    """
    def __init__(self, G, sources=list(), *args, **kwargs):
        self.G = G
        self.sources = sources or self.G.roots()
        # Properties common to all digraph searches
        self._edge_to = dict()  # v -> w : edge_to[w] = v
        self._visited = dict()
        for v in G:
            self._visited[v] = False
        self.search(*args, **kwargs)

    @abstractmethod
    def search(self, *args, **kwargs):
        pass

    def has_path_to(self, v):
        """has_path_to(v) returns True if there is a path from *any* s -> w.

        Parameters
        ----------
        v : vertex id
            A vertex id, typically int or str.
        """
        return self._visited[v]

    def path_to(self, v):
        """Returns path from source vertex to v.

        Parameters
        ----------
        v : vertex id
            A vertex id, typically int or str.

        Returns
        -------
        path : Stack of keys
            Stack of vertex ids in order of traversal.
        """
        if not self.has_path_to(v):
            return None
        path = Stack()
        x = v
        while x not in self.sources:
            path.push(x)
            x = self._edge_to[x].v
        path.push(x)
        return path

    def print_paths(self):
        """Print paths from each source to each other node."""
        for s in self.sources:
            for v in range(self.G.V):
                if self.has_path_to(v):
                    print(f"{s} -> {v} ({self._dist_to[v]:4.2f}): ", end='')
                    for x in self.path_to(v):
                        if x == s:
                            print(x, end='')
                        else:
                            print('-' + str(x), end='')
                    print()
                else:
                    print(f"{s} -> {v}:  not connected")


class DepthFirstSearch(GraphSearch):
    """Depth-first search class.

    Parameters
    ----------
    G : :obj:`Digraph`
    sources : iterable of vertex ids, optional
        Iterable of vertex ids from which to begin the search.

    .. note:: If no sources are given, DepthFirstSearch will run on all sources
        (nodes where indegree == 0).

    Attributes
    ----------
    G : :obj:`Digraph`
        The directed graph object to search.
    sources : iterable of vertex ids, optional
        Iterable of vertex ids from which to begin the search.
    """
    def __init__(self, G, sources=list()):
        super().__init__(G, sources)

    def search(self):
        for s in self.sources:
            self._dfsX(s)

    def _dfs(self, v):
        """Perform depth-first search, recursively."""
        self._visited[v] = True
        for e in self.G[v]:
            w = e.w
            if not self._visited[w]:
                self._edge_to[w] = e
                self._dfs(w)

    def _dfsX(self, v):
        """Perform depth-first search, with explicit stack."""
        path = Stack()
        path.push(v)
        self._visited[v] = True

        # Iterator of each adjacency list
        adj = self.G.iter_adjs()

        while path:
            v = path.peek()
            try:
                e = next(adj[v])
                w = e.w
                if not self._visited[w]:
                    self._edge_to[w] = e
                    self._visited[w] = True
                    path.push(w)
            except StopIteration:
                path.pop()


class DirectedCycle(GraphSearch):
    """Directed cycle search class.

    Parameters
    ----------
    G : :obj:`Digraph`
       The directed graph object to search.

    Attributes
    ----------
    G : :obj:`Digraph`
        The directed graph object to search.
    cycle : :obj:`Stack`
        Iterable of vertices on the cycle, if found.
    has_cycle : bool
        True if digraph `G` has a cycle

    .. note:: DirectedCycle does not care *which* cycle it finds.
    """
    def __init__(self, G):
        self.cycle = Stack()
        self._on_stack = dict()
        super().__init__(G)

    def search(self):
        """Find a cycle, if one exists."""
        for v in self.G:
            if not (self._visited[v] or self.cycle):
                self._dfsX(v)

    @property
    def has_cycle(self):
        """Returns True if Digraph has a directed cycle."""
        return bool(self.cycle)

    def _dfs(self, v):
        """Recursive depth-first search from vertex `v` until cycle is found."""
        self._visited[v] = True
        self._on_stack[v] = True

        for e in self.G[v]:
            w = e.w
            if not self._visited[w]:
                # Recur
                self._edge_to[w] = e
                self._dfs(w)
            elif self._on_stack[w]:
                # Trace back through the cycle
                f = e
                while f.w != w:
                    self.cycle.push(f)
                    f = self._edge_to[f.w]
                self.cycle.push(f)
                return

        # "pop" the item off the stack
        self._on_stack[v] = False

    def _dfsX(self, v):
        """Perform depth-first search, with explicit stack."""
        # Iterator of each adjacency list
        adj = self.G.iter_adjs()

        path = Stack()
        path.push(v)
        self._on_stack[v] = True
        self._visited[v] = True

        while path:
            v = path.peek()
            try:
                e = next(adj[v])
                w = e.w
                if not self._visited[w]:
                    path.push(w)
                    self._on_stack[w] = True
                    self._visited[w] = True
                    self._edge_to[w] = e
                elif self._on_stack[w]:
                    # Trace back through the cycle
                    f = e
                    while f.w != w:
                        self.cycle.push(f)
                        f = self._edge_to[f.w]
                    self.cycle.push(f)
                    return
            except StopIteration:
                path.pop()
                self._on_stack[v] = False


# TODO remove in favor of queue-based TopologicalOrder?
class DepthFirstOrder(GraphSearch):
    """Depth-first search to find vertex orders.

    Parameters
    ----------
    G : :obj:`Digraph`

    Attributes
    ----------
    G : :obj:`Digraph`
        The directed graph object to search.
    preorder : iterable of keys
        Order of node traversal *before* recursion
    postorder : iterable of keys
        Order of node traversal *after* recursion
    reverse_post : iterable of keys
        Reversed order of node traversal *after* recursion
    """
    def __init__(self, G):
        # Track the graph orders
        self.preorder = Queue()   # graph order before recursion
        self.postorder = Queue()  # graph order after recursion
        super().__init__(G)

    def search(self):
        for s in self.sources:
            self._dfsX(s)

    @property
    def reverse_post(self):
        """Return the reverse post-order of the digraph."""
        rev = Stack()
        for v in self.postorder:
            rev.push(v)
        return rev

    def _dfs(self, v):
        """Perform depth-first search, recursively. Record the orders."""
        self._visited[v] = True

        self.preorder.enqueue(v)  # preorder order

        for e in self.G[v]:
            w = e.w
            if not self._visited[w]:
                self._edge_to[w] = e
                self._dfs(w)

        self.postorder.enqueue(v)

    def _dfsX(self, v):
        """Perform depth-first search with explicit stack."""
        path = Stack()
        path.push(v)
        self._visited[v] = True
        self.preorder.enqueue(v)  # preorder order

        # Iterator of each adjacency list
        adj = self.G.iter_adjs()

        while path:
            v = path.peek()
            try:
                e = next(adj[v])
                w = e.w
                if not self._visited[w]:
                    self._edge_to[w] = e
                    self._visited[w] = True
                    path.push(w)
                    self.preorder.enqueue(w)  # preorder order
            except StopIteration:
                path.pop()
                self.postorder.enqueue(v)


def TopologicalOrder(G):
    """Topological order of a digraph.

    Parameters
    ----------
    G : :obj:`Digraph`
        The directed graph object.

    Returns
    ----------
    order : iterable of keys
        The topological order of the graph, if it exists. None otherwise.
    """
    order = None
    finder = DirectedCycle(G)
    if not finder.has_cycle:
        dfs = DepthFirstOrder(G)
        order = dfs.reverse_post
    return order

class BreadthFirstSearch(GraphSearch):
    """Breadth-first search class.

    Parameters
    ----------
    G : :obj:`Digraph`
        The directed graph object to search.
    sources : iterable of vertex ids, optional
        Iterable of vertex ids from which to begin the search.
    ordered : bool, optional, default=False
        Traverse the nodes in a specific order.
    kind : str in {'min, 'max'}, optional, default='min'
        How to choose the next node to traverse when outdegree > 1.

    Attributes
    ----------
    G : :obj:`Digraph`
        The directed graph object to search.
    sources : iterable
        Iterable of given sources, or vertices with indegree 0.
    all_paths : list
        List of all vertices touched during BFS.
    """
    def __init__(self, G, sources=None, ordered=False, kind='min'):
        self.all_paths = list()
        super().__init__(G, sources, ordered=ordered, kind=kind)

    def search(self, ordered=False, kind='min'):
        if ordered:
            self._ordered_bfs(kind)
        else:
            self._bfs()

    def _bfs(self):
        """Traverse all vertices breadth-first."""
        available = Queue(self.sources)

        while available:
            v = available.dequeue()
            self.all_paths.append(v)
            self._visited[v] = True

            for e in self.G[v]:
                w = e.w
                if not self._visited[w]:
                    self._visited[w] = True
                    self._edge_to[w] = e
                    available.enqueue(w)

    def _ordered_bfs(self, kind):
        """Traverse graph breadth-first, choosing minimum node id first.

        .. note:: will only find a complete path for a connected, acyclic
        graph.
        """
        # NOTE indegree is the only reference to Digraphs, specifically.
        prereqs = self.G.indegree.copy()  # mutable copy
        available = PriorityQueue(self.sources, kind='min')

        while available:
            v = available.dequeue()  # take min value
            self.all_paths.append(v)
            self._visited[v] = True

            for e in self.G[v]:
                w = e.w
                if prereqs[w] == 1:
                    self._visited[w] = True
                    self._edge_to[w] = e
                    available.enqueue(w)
                prereqs[w] -= 1


#------------------------------------------------------------------------------
#        Weighted Searches
#------------------------------------------------------------------------------
class AcyclicPath(GraphSearch):
    """Find the shortest or longest paths in a DAG.

    If the Digraph is not acyclic, AcyclicPath finds the max/minima paths from
    a source `s` to all other vertices `v` in the Digraph.

    Parameters
    ----------
    G : :obj:`Digraph`
        The directed graph object to search.
    s : key
        Single source vertex from which to find shortest paths.
    kind : str in {'min', 'max'}, optional, default='min'
        Choose whether to find the minimum path, or the maximum
    """
    def __init__(self, G, s, kind='min'):
        self._op = operator.gt if kind == 'min' else operator.lt
        self._dist_to = dict()
        for v in G:
            self._dist_to[v] = INF if kind == 'min' else M_INF
        self._dist_to[s] = 0.0
        super().__init__(G, [s])

    def search(self):
        topo = TopologicalOrder(self.G)
        if not topo:
            raise TypeError('Graph is not acyclic!')
        for v in topo:
            self._visited[v] = True
            for e in self.G[v]:
                self._relax(e)

    def dist_to(self, v):
        return self._dist_to[v]

    def _relax(self, e):
        """Relax a DirectedEdge if you find a *longer* path."""
        if self._op(self._dist_to[e.w], self._dist_to[e.v] + e.weight):
            self._dist_to[e.w] = self._dist_to[e.v] + e.weight
            self._edge_to[e.w] = e

#==============================================================================
#==============================================================================
