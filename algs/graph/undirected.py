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

from algs.basics import Bag, Stack, Queue


# -----------------------------------------------------------------------------
#         Abstract Base Classes
# -----------------------------------------------------------------------------
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
        if V < 0:
            raise ValueError(f"Number of vertices {V=} must be > 0!")
        self.V = V
        self.E = 0

    def _validate_vertex(self, v):
        if not (0 <= v < self.V):
            raise ValueError(f"Vertex index {v=} must be between 0 and {self.V=}!")

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


class Search(ABC):
    # An abstract base class of graph searches.
    """
    Attributes
    ----------
    G : :obj:`Graph`
        The graph over which to search.
    s : int
        The index of the source vertex.
    """

    def __init__(self, G, s=0):
        """
        Parameters
        ----------
        G : :obj:`Graph`
            The graph over which to search.
        s : int, optional
            The index of the source vertex.
        """
        self.G = G
        self.s = s

    @abstractmethod
    def marked(self, v):
        """Return True if `v` is connected to `s`."""
        pass

    @abstractmethod
    def count(self):
        """Return the number of vertices connected to `s`."""
        pass


class Paths(ABC):
    # An abstract base class for finding paths through a graph.
    __doc__ = Search.__doc__
    __init__ = Search.__init__

    @abstractmethod
    def has_path_to(self, v):
        """Return True if there is a path from `s` to `v`."""
        pass

    @abstractmethod
    def path_to(self, v):
        """Return an iterable of the vertices on the path from `s` to `v`."""
        pass


# -----------------------------------------------------------------------------
#         Concrete Classes
# -----------------------------------------------------------------------------
class Graph(AGraph):
    __doc__ = f"""Implements an undirected graph using adjacency lists.
        {AGraph.__doc__}"""

    def __init__(self, V):
        super().__init__(V)
        self._adj = [Bag() for _ in range(V)]

    def adj(self, v):
        self._validate_vertex(v)
        return self._adj[v]

    def add_edge(self, v, w):
        self._validate_vertex(v)
        self._validate_vertex(w)
        self._adj[v].add(w)
        self._adj[w].add(v)
        self.E += 1


class DepthFirstSearch(Search):
    __doc__ = f"""Implements depth-first search.
        {Search.__doc__}"""

    def __init__(self, G, s):
        super().__init__(G, s)
        self._marked = G.V * [False]
        self._count = 0
        self._dfs(s)

    def marked(self, v):
        return self._marked[v]

    def count(self):
        return self._count

    def _dfs(self, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        self._count += 1
        for w in self.G.adj(v):
            if not self._marked[w]:
                self._dfs(w)


class DepthFirstPaths(Paths):
    __doc__ = f"""Implements depth-first search to return a path.
        {Paths.__doc__}"""

    def __init__(self, G, s):
        super().__init__(G, s)
        self._marked = G.V * [False]
        self._edge_to = G.V * [0]  # last vertex on known path to this one
        self._dfs(s)

    def _dfs(self, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        for w in self.G.adj(v):
            if not self._marked[w]:
                self._edge_to[w] = v
                self._dfs(w)

    def has_path_to(self, v):
        return self._marked[v]

    def path_to(self, v):
        if not self.has_path_to(v):
            return None
        path = Stack()
        x = v
        while x != self.s:
            path.push(x)
            x = self._edge_to[x]
        path.push(self.s)
        return path


class BreadthFirstPaths(Paths):
    __doc__ = f"""Implements breadth-first search to find shortest paths.
        {Paths.__doc__}"""

    def __init__(self, G, s):
        super().__init__(G, s)
        self._marked = G.V * [False]
        self._edge_to = G.V * [0]  # last vertex on known path to this one
        self._bfs(s)

    def _bfs(self, v):
        """Perform depth-first search recursively from vertex `v`."""
        q = Queue()
        self._marked[v] = True
        q.enqueue(self.s)
        while not q.is_empty:
            v = q.dequeue()
            for w in self.G.adj(v):
                if not self._marked[w]:
                    self._edge_to[w] = v
                    self._marked[w] = True
                    q.enqueue(w)

    def has_path_to(self, v):
        return self._marked[v]

    def path_to(self, v):
        if not self.has_path_to(v):
            return None
        path = Stack()
        x = v
        while x != self.s:
            path.push(x)
            x = self._edge_to[x]
        path.push(self.s)
        return path


# -----------------------------------------------------------------------------
#         Functions
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
#         Tests
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    from pathlib import Path
    filename = Path('../data/tinyG.txt')
    G = Graph.fromfile(filename)
    print(G)

    # Test search
    print('----- DFS -----')

    def search(G, s):
        """Search the graph from vertex `s`."""
        the_search = DepthFirstSearch(G, s)
        for v in range(G.V):
            if the_search.marked(v):
                print(f"{v} ", end='')
        print()
        if the_search.count() != G.V:
            print('NOT ', end='')
        print('connected.')
        return the_search

    search(G, 0)
    search(G, 9)

    # Test paths
    filename = Path('../data/tinyCG.txt')
    G = Graph.fromfile(filename)
    print(G)

    def paths(G, s, kind='DFS'):
        """Search the graph from vertex `s`, returning the paths."""
        if kind == 'DFS':
            Path = DepthFirstPaths
        elif kind == 'BFS':
            Path = BreadthFirstPaths
        else:
            raise ValueError(f"{kind=} is unrecognized!")
        the_search = Path(G, s)
        for v in range(G.V):
            print(f"{s:2d}->{v:2d}: ", end='')
            if the_search.has_path_to(v):
                for x in the_search.path_to(v):
                    if x == s:
                        print(x, end='')
                    else:
                        print(f"-{x}", end='')
            print()

    print('----- DFS Paths -----')
    paths(G, 0, kind='DFS')
    print('----- BFS Paths -----')
    paths(G, 0, kind='BFS')

# =============================================================================
# =============================================================================
