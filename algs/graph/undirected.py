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
from algs.search import HashST


# -----------------------------------------------------------------------------
#         Abstract Base Classes
# -----------------------------------------------------------------------------
class UndirectedGraph(ABC):
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
            E = int(fp.readline())
            G = cls(V)
            for line in fp.readlines():
                v, w = line.strip().split()
                G.add_edge(int(v), int(w))
            assert E == G.E
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
class Graph(UndirectedGraph):
    __doc__ = f"""Implements an undirected graph using adjacency lists.
        {UndirectedGraph.__doc__}"""
    # See p 526

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

    # Exercise 4.1.3
    def copy(self):
        """Make a deep copy of the graph structure."""
        g = self.__class__(self.V)  # initializes array of empty Bags.
        for v in range(self.V):
            # NOTE WRONG CODE makes a reference, not a copy:
            #   g._adj[v] = self._adj[v]
            #   (G._adj[v] is G.copy()._adj[v]) == True
            # Correct code makes a copy:
            for w in self._adj[v]:
                g._adj[v].add(w)
        return g


class DepthFirstSearch(Search):
    __doc__ = f"""Implements depth-first search.
        {Search.__doc__}"""
    # See p 531

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


# Algorithm 4.1
class DepthFirstPaths(Paths):
    __doc__ = f"""Implements depth-first search to return a path.
        {Paths.__doc__}"""

    def __init__(self, G, s):
        super().__init__(G, s)
        self._marked = G.V * [False]
        self._edge_to = G.V * [None]  # last vertex on known path to this one
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


# Algorithm 4.2
class BreadthFirstPaths(Paths):
    __doc__ = f"""Implements breadth-first search to find shortest paths.
        {Paths.__doc__}"""

    def __init__(self, G, s):
        super().__init__(G, s)
        self._marked = G.V * [False]
        self._edge_to = G.V * [None]  # last vertex on known path to this one
        self._dist_to = G.V * [None]  # Exercise 4.1.13
        self._bfs(s)

    def _bfs(self, v):
        """Perform depth-first search recursively from vertex `v`."""
        q = Queue()
        self._marked[v] = True
        self._dist_to[v] = 0
        q.enqueue(self.s)
        while not q.is_empty:
            v = q.dequeue()
            for w in self.G.adj(v):
                if not self._marked[w]:
                    self._edge_to[w] = v
                    self._marked[w] = True
                    self._dist_to[w] = self._dist_to[v] + 1
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

    # Exercise 4.1.13
    def dist_to(self, v):
        """Return the distance from source to `v`. None if not connected."""
        return self._dist_to[v]


# Algorithm 4.3
class CC:
    """Implements a connected components depth-first search.

    Attributes
    ----------
    G : :obj:`Graph`
        The graph to analyze.
    """

    def __init__(self, G):
        self.G = G
        self._marked = G.V * [False]
        self._id = G.V * [0]
        self._count = 0
        # Perform DFS for *every* source vertex.
        for s in range(G.V):
            if not self._marked[s]:
                self._dfs(s)
                self._count += 1

    def _dfs(self, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        self._id[v] = self._count
        for w in self.G.adj(v):
            if not self._marked[w]:
                self._dfs(w)

    def connected(self, v, w):
        """Return True if `v` and `w` are connected."""
        # Same as quick-find!
        return self._id[v] == self._id[w]

    def id(self, v):
        """Return the component identifier for vertex `v` in `[0, count-1]`."""
        return self._id[v]

    def count(self):
        """The number of connected components."""
        return self._count


class SymbolGraph:
    """Implements a symbol graph."""
    # See p 552

    def __init__(self):
        self._st = HashST()  # map : str -> int
        self._keys = None    # map : int -> str
        self.G = None

    @classmethod
    def fromfile(cls, filename, delim=' '):
        """Construct a SymbolGraph from a delimited text file containing an
        adjacency list for the graph.

        Parameters
        ----------
        filename : str
            The name of the adjacency list file to process.
        delim : char, optional
            The character on which to split words.

        Returns
        -------
        res : :obj:`SymbolGraph`
            The SymbolGraph defined by the adjaceny list file.
        """
        sg = cls()
        # First pass to add all vertices to the symbol table
        with open(filename, 'r') as fp:
            for line in fp.readlines():
                words = line.strip().split(delim)
                for word in words:
                    if word not in sg._st:
                        sg._st[word] = sg._st.size()  # unique index

        # Build inverted index
        V = sg._st.size()
        sg._keys = V * [None]
        for name in sg._st.keys():
            sg._keys[sg._st[name]] = name

        # Second pass to build the graph
        sg.G = Graph(V)
        with open(filename, 'r') as fp:
            for line in fp.readlines():
                words = line.strip().split(delim)
                v = sg._st[words[0]]
                for w in words[1:]:
                    sg.G.add_edge(v, sg._st[w])

        return sg

    def __contains__(self, k):
        """Return True if `k` is a vertex."""
        return self._st.contains(k)

    def index(self, k):
        """Return the index associated with `k`."""
        return self._st[k]

    def name(self, v):
        """Return the name associated with vertex index `v`."""
        return self._keys[v]

    # aliases
    def contains(self, k):
        return self.__contains__(k)


class Cycle(Search):
    __doc__ = f"""Implements depth-first search to find a cycle.
        {Search.__doc__}"""
    # See p 547

    def __init__(self, G, s):
        self.G = G
        self.s = s
        self._marked = G.V * [False]
        self.has_cycle = False
        self._dfs(s)

    def _dfs(self, v, u):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        for w in self.G.adj(v):
            if not self._marked[w]:
                self._dfs(w, v)
            elif w != u:
                self.has_cycle = True


class TwoColor(Search):
    __doc__ = f"""Implements depth-first search to determine if a graph is
        bipartite.
        {Search.__doc__}"""
    # See p 547

    def __init__(self, G, s):
        self.G = G
        self.s = s
        self._marked = G.V * [False]
        self._color = G.V * [False]
        self.is_bipartite = False
        self._dfs(s)

    def _dfs(self, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        for w in self.G.adj(v):
            if not self._marked[w]:
                self._color[w] = not self._color[v]
                self._dfs(w)
            elif self._color[w] == self._color[v]:
                self.is_bipartite = False


# -----------------------------------------------------------------------------
#         Client Functions
# -----------------------------------------------------------------------------
# Define some functions for use with graphs that would be too cumbersome to
# maintain in the basic API. See p 523.
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


def dfs(G, s):
    """Search the graph from vertex `s`."""
    # See p 529
    search = DepthFirstSearch(G, s)
    for v in range(G.V):
        if search.marked(v):
            print(f"{v} ", end='')
    print()
    if search.count() != G.V:
        print('NOT ', end='')
    print('connected.')
    return search


def paths(G, s, kind='DFS'):
    """Search the graph from vertex `s`, returning the paths."""
    # See p 535
    if kind == 'DFS':
        search = DepthFirstPaths(G, s)
    elif kind == 'BFS':
        search = BreadthFirstPaths(G, s)
    else:
        raise ValueError(f"{kind=} is unrecognized!")
    for v in range(G.V):
        print(f"{s:2d}->{v:2d}: ", end='')
        if search.has_path_to(v):
            for x in search.path_to(v):
                if x == s:
                    print(x, end='')
                else:
                    print(f"-{x}", end='')
        print()


def find_components(G):
    """Compute the connected components in the graph."""
    # See p 543
    cc = CC(G)
    M = cc.count()
    print(f"{M} components")
    components = [Bag() for _ in range(M)]
    for v in range(G.V):
        components[cc.id(v)].add(v)
    for i in range(M):
        print(f"{i}: ", end='')
        for v in components[i]:
            print(f"{v} ", end='')
        print()


def print_adj(sg, s):
    """Print the adjacency list of the source."""
    # See p 550
    print(s)
    for w in sg.G.adj(sg.index(s)):
        print(' ', sg.name(w))


def degrees_of_separation(sg, source, sink):
    """Return the shortest path from source to sink in a symbol graph."""
    # See p 555
    if source not in sg:
        raise ValueError(f"{repr(source)} not in graph!")
    s = sg.index(source)
    bfs = BreadthFirstPaths(sg.G, s)
    if sink in sg:
        print(source)
        t = sg.index(sink)
        if bfs.has_path_to(t):
            for v in bfs.path_to(t):
                print(' ', sg.name(v))
        else:
            print('Not connected.')
    else:
        raise ValueError(f"{repr(sink)} not in graph!")


# -----------------------------------------------------------------------------
#         Tests
# -----------------------------------------------------------------------------
# TODO tests/test_graph.py
if __name__ == "__main__":
    from pathlib import Path
    G = Graph.fromfile(Path('../data/tinyG.txt'))
    print(G)

    # Test search
    print('----- DFS -----')
    dfs(G, 0)
    dfs(G, 9)

    # Test paths
    print('----- Connected Graph -----')
    G = Graph.fromfile(Path('../data/tinyCG.txt'))
    print(G)
    print('----- DFS Paths -----')
    paths(G, 0, kind='DFS')
    print('----- BFS Paths -----')
    paths(G, 0, kind='BFS')

    # Test connected components
    print('----- CC -----')
    G = Graph.fromfile(Path('../data/tinyG.txt'))
    find_components(G)

    # Test connected components
    print('----- SymbolGraph -----')
    sg = SymbolGraph.fromfile(Path('../data/routes.txt'))
    print('--- adjacency lists ---')
    print_adj(sg, 'JFK')
    print_adj(sg, 'LAX')
    print('--- shortest paths ---')
    degrees_of_separation(sg, 'JFK', 'LAS')
    degrees_of_separation(sg, 'JFK', 'DFW')

    # sg = SymbolGraph.fromfile(Path('../data/movies.txt'), delim='/')
    # print('--- adjacency lists ---')
    # print_adj(sg, 'Top Gun (1986)')
    # print('--- shortest paths ---')
    # degrees_of_separation(sg, 'Animal House (1978)', 'Titanic (1997)')
    # degrees_of_separation(sg, 'Bacon, Kevin', 'Cruise, Tom')

    # Test dist_to
    G = Graph.fromfile(Path('../data/tinyG2.txt'))
    bfs = BreadthFirstPaths(G, 0)
    assert ([bfs.dist_to(x) for x in range(G.V)] 
            == [0, None, 1, 2, None, 1, 1, None, None, None, 2, None])

    # Test copy
    G2 = G.copy()
    for v in range(G.V):
        assert G.adj(v) == G2.adj(v)
        assert G._adj[v] is not G2._adj[v]

# =============================================================================
# =============================================================================
