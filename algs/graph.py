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

from abc import ABC, abstractmethod

from .basics import Stack, Queue, PriorityQueue

class Digraph():
    """Directed graph represented as a dictionary of vertices.

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
        self.adj = dict()       # vertex adjacency list
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

    def vertices(self):
        """Iterable of all the vertex keys in the Digraph."""
        yield from self.adj.keys()

    # def iter_adj(self):
    #     return {v: iter(self.adj[v]) for v in self.adj}

    def add_edge(self, a, b):
        """Add edge between two vertex ids.

        Parameters
        ----------
        a : key
            Starting vertex id
        b : key
            Ending vertex id
        """
        self.E += 1

        if a not in self.adj:
            self._init_vertex(a)
        self.adj[a].append(b)

        if b not in self.indegree:
            self._init_vertex(b)
        self.indegree[b] += 1

    def reverse(self):
        """Return the reverse of the Digraph."""
        rev = Digraph()
        for v in self.adj:
            for w in self.adj[v]:
                rev.add_edge(w, v)
        return rev

    def __getitem__(self, v):
        return self.adj[v]

    def __iter__(self):
        yield from self.vertices()

    def __repr__(self):
        return '<Digraph: ' + self.__str__() + '>'

    def __str__(self):
        return str(self.adj)


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
        return '{:d}->{:d} ({:3.2g})'.format(self.v, self.w, self.weight)


class EdgeWeightedDigraph():
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
        yield from the_edges

    def vertices(self):
        """Iterable of all the vertex keys in the Digraph."""
        yield from self.adj.keys()

    def add_edge(self, a, b, w):
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
            x = self._edge_to[x]
        path.push(x)
        return path

    def print_paths(self):
        """Print paths from each source to each other node."""
        for s in self.sources:
            for v in range(self.G.V):
                if self.has_path_to(v):
                    print("{:<2d} -> {:2d}:  ".format(s, v), end='')
                    for x in self.path_to(v):
                        if x == s:
                            print(x, end='')
                        else:
                            print('-' + str(x), end='')
                    print()
                else:
                    print("{:<2d} -> {:2d}:  not connected".format(s, v))


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
        for w in self.G[v]:
            if not self._visited[w]:
                self._edge_to[w] = v
                self._dfs(w)

    def _dfsX(self, v):
        """Perform depth-first search, with explicit stack."""
        path = Stack()
        path.push(v)
        self._visited[v] = True

        # Iterator of each adjacency list
        adj = {v: iter(self.G[v]) for v in self.G}

        while path:
            v = path.peek()
            try:
                w = next(adj[v])
                if not self._visited[w]:
                    self._edge_to[w] = v
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

        for w in self.G[v]:
            if self.cycle:
                return
            elif not self._visited[w]:
                # Recur
                self._edge_to[w] = v
                self._dfs(w)
            elif self._on_stack[w]:
                # Trace back through the cycle
                x = v
                while x != w:
                    self.cycle.push(x)
                    x = self._edge_to[x]
                self.cycle.push(w)
                self.cycle.push(v)  # store the first node twice

        # "pop" the item off the stack
        self._on_stack[v] = False

    def _dfsX(self, v):
        """Perform depth-first search, with explicit stack."""
        # Iterator of each adjacency list
        adj = {v: iter(self.G[v]) for v in self.G}

        path = Stack()
        path.push(v)
        self._on_stack[v] = True
        self._visited[v] = True

        while path:
            v = path.peek()
            try:
                w = next(adj[v])
                if not self._visited[w]:
                    path.push(w)
                    self._on_stack[w] = True
                    self._visited[w] = True
                    self._edge_to[w] = v
                elif self._on_stack[w]:
                    # Trace back through the cycle
                    x = v
                    while x != w:
                        self.cycle.push(x)
                        x = self._edge_to[x]
                    self.cycle.push(w)
                    self.cycle.push(v)  # store the first node twice
            except StopIteration:
                path.pop()
                self._on_stack[v] = False

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
    prerank : iterable of keys
        prerank[v] returns the `preorder` ranking of vertex with key `v`.
    postrank : iterable of keys
        postrank[v] returns the `postorder` ranking of vertex with key `v`.
    """
    def __init__(self, G):
        # Track the graph orders
        self.preorder = Queue()   # graph order before recursion
        self.postorder = Queue()  # graph order after recursion
        self.prerank = dict()
        self.postrank = dict()
        self._precounter = 0
        self._postcounter = 0
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
        self.prerank[v] = self._precounter
        self._precounter += 1

        for w in self.G[v]:
            if not self._visited[w]:
                self._edge_to[w] = v
                self._dfs(w)

        self.postorder.enqueue(v)
        self.postrank[v] = self._postcounter
        self._postcounter += 1

    def _dfsX(self, v):
        """Perform depth-first search with explicit stack."""
        path = Stack()
        path.push(v)
        self._visited[v] = True
        self.preorder.enqueue(v)  # preorder order
        self.prerank[v] = self._precounter
        self._precounter += 1

        # Iterator of each adjacency list
        adj = {v: iter(self.G[v]) for v in self.G}

        while path:
            v = path.peek()
            try:
                w = next(adj[v])
                if not self._visited[w]:
                    self._edge_to[w] = v
                    self._visited[w] = True
                    path.push(w)
                    self.preorder.enqueue(w)  # preorder order
                    self.prerank[w] = self._precounter
                    self._precounter += 1
            except StopIteration:
                path.pop()
                self.postorder.enqueue(v)
                self.postrank[v] = self._postcounter
                self._postcounter += 1


class TopologicalOrder():
    """Topological order of a digraph.

    Parameters
    ----------
    G : :obj:`Digraph`
        The directed graph object.

    Attributes
    ----------
    G : :obj:`Digraph`
        The directed graph object.
    has_order : bool
        True if the graph is acyclic.
    order : iterable of keys
        The topological order of the graph, if it exists. None otherwise.
    rank : dict of ints
        rank[v] returns the ranking of vertex with key `v`.
    """
    def __init__(self, G):
        self.G = G
        self.order = None
        self.rank = None
        finder = DirectedCycle(self.G)
        if not finder.has_cycle:
            dfs = DepthFirstOrder(self.G)
            self.order = dfs.reverse_post
            self.rank = dict()
            for i, v in enumerate(self.order):
                self.rank[v] = i

    @property
    def has_order(self):
        return bool(self.order)


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

            for w in self.G[v]:
                if not self._visited[w]:
                    self._visited[w] = True
                    self._edge_to[w] = v
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

            for w in self.G[v]:
                if prereqs[w] == 1:
                    self._visited[w] = True
                    self._edge_to[w] = v
                    available.enqueue(w)
                prereqs[w] -= 1


#==============================================================================
#==============================================================================
