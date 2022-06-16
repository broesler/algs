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
from collections import deque
from tqdm import tqdm

from algs.basics import Bag, Stack, Queue
from algs.search import Set, HashST
from algs import WeightedQuickUnionUF


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

    def __init__(self, V=0, edges=None):
        if V < 0:
            raise ValueError(f"Number of vertices {V=} must be > 0!")
        self.V = V
        self.E = 0
        edges = edges or []
        try:
            for v, w in edges:
                self.add_edge(v, w)
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             'expects an iterable of tuples.')

    @classmethod
    def fromfile(cls, filename, verbose=False, **kwargs):
        """Construct the graph structure from a file."""
        with open(filename, 'r') as fp:
            V = int(fp.readline())
            E = int(fp.readline())
            G = cls(V=V, **kwargs)
            iters = fp.readlines()
            if verbose:
                iters = tqdm(iters)
            for line in iters:
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

    # Exercise 4.1.4
    def has_edge(self, v, w):
        """Return True if an edge from `v` to `w` exists."""
        return w in self.adj(v)

    @abstractmethod
    def vertices(self):
        """Return an iterable over the vertices."""
        pass

    @abstractmethod
    def edges(self):
        """Return an iterable over the edges as pairs of vertices."""
        pass

    def __str__(self):
        s = f"{self.V} vertices, {self.E} edges\n"
        for v in self.vertices():
            s += f"{v}: " + ' '.join(str(w) for w in self.adj(v)) + '\n'
        return s.strip()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"


class GraphSearch(ABC):
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
    __doc__ = GraphSearch.__doc__
    __init__ = GraphSearch.__init__

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
    __doc__ = f"""Implements a graph using an array of adjacency lists.
    {UndirectedGraph.__doc__}"""
    # See p 526

    def __init__(self, V=0, edges=None, parallel=True, self_loops=True):
        self._PARALLEL = bool(parallel)
        self._SELF_LOOPS = bool(self_loops)
        if self._PARALLEL:
            self._adj = [Bag() for _ in range(V)]
        else:
            # Exercise 4.1.5 no parallel edges
            # NOTE that using `set` breaks the ordering of `adj(v)`
            self._adj = [set() for _ in range(V)]
        super().__init__(V=V, edges=edges)

    __init__.__doc__ = f"""{UndirectedGraph.__init__.__doc__}
    parallel : bool, optional
        If True, allow parallel edges.
    self_loops : bool, optional
        If True, allow self-loops.
    """

    def _validate_vertex(self, v):
        if not (0 <= v < self.V):
            raise ValueError((f"Vertex index {v=} must be "
                              f"between 0 and {self.V=}!"))

    def vertices(self):
        return range(self.V)

    def edges(self):
        e = set()
        for v in self.vertices():
            for w in self._adj[v]:
                # Only add single direction
                if (w, v) not in e:
                    e.add((v, w))
        return e

    def adj(self, v):
        self._validate_vertex(v)
        return self._adj[v]

    def add_edge(self, v, w):
        self._validate_vertex(v)
        self._validate_vertex(w)
        # Exercise 4.1.5
        if not self._SELF_LOOPS and v == w:
            raise ValueError(f"{v} == {w}! No self-loops allowed.")
        if not self.has_edge(v, w):
            self.E += 1
        self._adj[v].add(w)
        self._adj[w].add(v)

    # Exercise 4.1.3
    def copy(self):
        """Make a deep copy of the graph structure."""
        g = self.__class__(self.V)
        g.E = self.E
        for v in range(self.V):
            for w in self._adj[v]:
                g._adj[v].add(w)
        return g

    # Exercise 4.1.24 (inspiration)
    def subgraph(self, vertices):
        """Return the subgraph containing the `vertices`.

        .. note:: This method re-maps the vertices to [0, 1, ...len(vertices)]
        for array indexing, so although the structure of the subgraph will
        match that of the original, the vertex names will be different.
        """
        vertices = Set(vertices)  # use ordered set for ranking adjacents
        g = self.__class__(len(vertices))
        for v, w in self.edges():
            if v in vertices and w in vertices:
                g.add_edge(vertices.rank(v), vertices.rank(w))
        return g


class STGraph(UndirectedGraph):
    __doc__ = f"""Implements a graph using a symbol table of adjacency lists.
    {UndirectedGraph.__doc__}"""
    # See p 557 and
    # <https://introcs.cs.princeton.edu/java/45graph/Graph.java.html>

    def __init__(self, V=None, edges=None, parallel=True, self_loops=True):
        self._PARALLEL = bool(parallel)
        self._SELF_LOOPS = bool(self_loops)
        self._adj = HashST()
        self.V = 0
        if V is not None:
            try:
                # iterate over V itself
                for v in V:
                    self.add_vertex(v)
            except TypeError:
                # If V is an integer, number the vertices accordingly
                for v in range(V):
                    self.add_vertex(v)
        super().__init__(V=self.V, edges=edges)

    __init__.__doc__ = f"""{UndirectedGraph.__init__.__doc__}
    parallel : bool, optional
        If True, allow parallel edges.
    self_loops : bool, optional
        If True, allow self-loops.
    """

    def _validate_vertex(self, v):
        if not self.has_vertex(v):
            raise ValueError(f"Vertex {v=} does not exist!")

    def has_vertex(self, v):
        return v in self._adj

    def vertices(self):
        return self._adj.keys()

    def edges(self):
        e = set()
        for v in self.vertices():
            for w in self._adj[v]:
                # Only add single direction
                if (w, v) not in e:
                    e.add((v, w))
        return e

    def adj(self, v):
        self._validate_vertex(v)
        return self._adj[v]

    def add_vertex(self, v):
        """Add a vertex to the graph."""
        if not self.has_vertex(v):
            if self._PARALLEL:
                self._adj[v] = Bag()
            else:
                self._adj[v] = set()
            self.V += 1

    def add_edge(self, v, w):
        if v not in self._adj:
            self.add_vertex(v)
        if w not in self._adj:
            self.add_vertex(w)
        # Exercise 4.1.5
        if not self._SELF_LOOPS and v == w:
            raise ValueError(f"{v} == {w}! No self-loops allowed.")
        if not self.has_edge(v, w):
            self.E += 1
        self._adj[v].add(w)
        self._adj[w].add(v)

    # Exercise 4.1.3
    def copy(self):
        """Make a deep copy of the graph structure."""
        return self.subgraph(self.vertices())

    # Exercise 4.1.3 + 4.1.24 (inspiration)
    def subgraph(self, vertices):
        """Make a deep copy of the subgraph containing the `vertices`."""
        vertices = set(vertices)
        g = self.__class__(vertices)
        for v in vertices:
            for w in self._adj[v]:
                if w in vertices:
                    g._adj[v].add(w)
        return g


class DepthFirstSearch(GraphSearch):
    __doc__ = f"""Implements depth-first search.
    {GraphSearch.__doc__}"""
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
        """Perform breadth-first search from vertex `v`."""
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
        # Same as DepthFirstPaths method
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


# Exercise 4.1.8
class UFSearch(GraphSearch):
    __doc__ = f"""Implements the graph search API using Union-Find.

    .. note:: This implementation is simple and efficient if we are only
    concerned with determining connectivity. The UF algorithm is also an
    *online* algorithm, as opposed to DFS which must preprocess the entire
    graph structure.
    {GraphSearch.__doc__}"""
    # See p 529

    def __init__(self, G, s):
        super().__init__(G, s)
        self._uf = WeightedQuickUnionUF(G.V)
        for v in G.vertices():
            for w in self.G.adj(v):
                if not self._uf.connected(v, w):
                    self._uf.union(v, w)

    def marked(self, v):
        return self._uf.connected(self.s, v)

    def count(self):
        # Return the size of the component to which the source belongs
        return self._uf._size[self._uf.find(self.s)]


# Exercise 4.1.10
class LeafDFS(GraphSearch):
    __doc__ = f"""Implements depth-first search to find a non-structural
    vertex, aka a leaf of a spanning tree rooted at the source.
    {GraphSearch.__doc__}"""

    def __init__(self, G, s):
        super().__init__(G, s)
        self._marked = G.V * [False]
        self._count = 0
        self._leaf = self._dfs(s)

    def marked(self, v):
        return self._marked[v]

    def count(self):
        return self._count

    def _dfs(self, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        self._count += 1
        if all([self._marked[x] for x in self.G.adj(v)]):
            return v
        for w in self.G.adj(v):
            if not self._marked[w]:
                return self._dfs(w)

    def leaf(self):
        return self._leaf


# Exercise 4.1.16
class GraphProperties:
    """A class to determine the geometric properties of a connected graph."""

    def __init__(self, G):
        if CC(G).count() > 1:
            raise ValueError('Graph must be connected!')
        self.G = G
        # pre-compute eccentricities and store in a symbol table (in case
        # vertices are not represented as integers)
        self._eccs = dict({v: self._ecc(v) for v in self.G.vertices()})
        self._dia = max(self._eccs.values())
        self._rad = min(self._eccs.values())

    def eccentricity(self, v):
        """The length of the shortest path from `v` to the furthest vertex from
        `v`, *i.e.* the maximum length of the shortest path to any vertex."""
        return self._eccs[v]

    def _ecc(self, v):
        # Compute the shortest path from v to every other vertex
        bfs = BreadthFirstPaths(self.G, v)
        return max([bfs.dist_to(x) for x in self.G.vertices()])

    def diameter(self):
        """The maximum eccentricity of any vertex."""
        return self._dia

    def radius(self):
        """The smallest eccentricity of any vertex."""
        return self._rad

    def center(self):
        """A vertex whose eccentricity is the radius."""
        for v in self.G.vertices():
            if self._eccs[v] == self._rad:
                return v

    def girth(self):
        """Return the length of the shortest cycle in the graph.
        If there are no cycles, the girth is infinite.

        The algorithm runs in O(V(V + E)) time, since all source vertices must
        be checked, and BFS runs in O(V + E) worst-case time. This runtime is
        an improvement over O(E(V + E)), since E ∈ [V-1, (V-1)V/2]."""
        # G is guaranteed to be connected, so only need to check one vertex
        m = float('inf')  # set "minimum" to maximum
        if not Cycle(self.G, 0).has_cycle:
            return m
        # Compute the shortest cycle: O(V(V + E))
        # TODO come up with example of graph where BFS would *not* find the
        # minimum cycle in a connected graph just by searching from one vertex.
        for v in self.G.vertices():
            bfs = MinCyclePath(self.G, v)
            m = min(m, bfs.cycle_length)
        return m


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
        self.sizes = [0]
        self._marked = G.V * [False]
        self._id = G.V * [0]
        self._count = 0
        # Perform DFS for *every* source vertex.
        for s in G.vertices():
            if not self._marked[s]:
                self._dfs(s)
                self._count += 1
                self.sizes.append(0)
        # Trim extra 0 if necessary
        self.sizes = self.sizes[:self._count]
        # assert sum(self.sizes) == self.G.V

    def _dfs(self, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        self._id[v] = self._count
        self.sizes[self._count] += 1
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

    def vertices(self, k):
        """Return an iterable of the vertices in the component with id `k`."""
        return (v for v, c in enumerate(self._id) if c == k)

    def size(self, k):
        """Return the size of the component with id `k`."""
        return self.sizes[k]


class SymbolGraph:
    """Implements a symbol graph."""
    # See p 552

    def __init__(self):
        self._st = HashST()  # map : str -> int
        self._keys = None    # map : int -> str
        self.G = None

    @classmethod
    def fromfile(cls, filename, *args, delim=' ', verbose=False, **kwargs):
        """Construct a SymbolGraph from a delimited text file containing an
        adjacency list for the graph.

        Parameters
        ----------
        filename : str
            The name of the adjacency list file to process.
        delim : char, optional
            The character on which to split words.
        verbose : bool, optional
            If True, print a progress bar while reading the file.

        Returns
        -------
        res : :obj:`SymbolGraph`
            The SymbolGraph defined by the adjaceny list file.
        """
        sg = cls(*args, **kwargs)
        # First pass to add all vertices to the symbol table
        with open(filename, 'r') as fp:
            iters = fp.readlines()
            if verbose:
                iters = tqdm(iters)
            for line in iters:
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

    @property
    def V(self):
        return self.G.V

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


class Cycle:
    __doc__ = f"""Implements depth-first search to find a cycle.
    {GraphSearch.__doc__}"""
    # See p 547

    class CycleFound(Exception):
        """Raise exception to break recursive calls once cycle is found."""
        pass

    def __init__(self, G, s):
        self.G = G
        self.s = s
        self.has_cycle = False
        self._marked = G.V * [False]
        try:
            self._dfs(s, s)
        except self.CycleFound:
            pass

    def _dfs(self, v, u):
        """Perform depth-first search recursively from vertex `v`.

        .. note:: `u` is the previously-seen vertex. If one of the adjacent
        vertices to `v` is marked, but is not the vertex from which we just
        came, we have a cycle.
        """
        self._marked[v] = True
        for w in self.G.adj(v):
            if not self._marked[w]:
                self._dfs(w, v)
            elif w != u:
                self.has_cycle = True
                raise self.CycleFound


class CyclePath(DepthFirstPaths):
    __doc__ = f"""Implements depth-first search to find a cyclic path.
    {GraphSearch.__doc__}"""

    class CycleFound(Exception):
        pass

    def __init__(self, G, s):
        self.G = G
        self.s = s
        self.has_cycle = False
        self._marked = G.V * [False]
        self._edge_to = G.V * [None]  # last vertex on known path to this one
        self._cycle_head = None  # start vertex of the cycle
        self._cycle_tail = None  # end vertex of the cycle
        try:
            self._dfs(s, s)
        except self.CycleFound:
            pass

    def _dfs(self, v, u):
        """Perform depth-first search recursively from vertex `v`.

        .. note:: `u` is the previously-seen vertex. If one of the adjacent
        vertices to `v` is marked, but is not the vertex from which we just
        came, we have a cycle.
        """
        self._marked[v] = True
        for w in self.G.adj(v):
            if not self._marked[w]:
                self._edge_to[w] = v
                self._dfs(w, v)
            elif w != u:
                self.has_cycle = True
                self._cycle_head = w
                self._cycle_tail = v
                raise self.CycleFound

    def cycle_path(self):
        """Return the path of the found cycle."""
        p = deque(self.path_to(self._cycle_tail))
        p.append(self._cycle_head)
        # Cycle may not include the source! Remove irrelevant vertices.
        while p[0] != p[-1]:
            p.popleft()
        return p


class MinCyclePath(BreadthFirstPaths):
    __doc__ = f"""Implements breadth-first search to find a minimum cycle.
    {GraphSearch.__doc__}"""

    def __init__(self, G, s):
        self.G = G
        self.s = s
        self.has_cycle = False
        self.cycle_length = float('inf')
        self._marked = G.V * [False]
        self._edge_to = G.V * [None]
        self._dist_to = G.V * [None]
        self._cycle_head = None  # start vertex of the cycle
        self._cycle_tail = None  # end vertex of the cycle
        # Run the search
        self._bfs(s)

    def _bfs(self, v):
        """Perform breadth-first search from vertex `v`."""
        q = Queue()
        self._marked[v] = True
        self._dist_to[v] = 0
        q.enqueue(v)
        while not q.is_empty:
            v = q.dequeue()
            for w in self.G.adj(v):
                if w == self._edge_to[v]:
                    continue
                if not self._marked[w]:
                    self._edge_to[w] = v
                    self._marked[w] = True
                    self._dist_to[w] = self._dist_to[v] + 1
                    q.enqueue(w)
                else:
                    self.has_cycle = True
                    d = self._dist_to[v] + self._dist_to[w] + 1
                    if d < self.cycle_length:
                        self._cycle_head = w
                        self._cycle_tail = v
                        self.cycle_length = d

    def cycle_path(self):
        """Return the path of the found cycle."""
        # BFS gives two paths: one each to head and tail.
        # Merge the paths to head and tail to remove all common ancestors
        # except the last that completes the cycle.
        p = deque(self.path_to(self._cycle_tail))
        q = deque(self.path_to(self._cycle_head))
        while len(p) > 2 and len(q) > 2 and p[0] == q[0] and p[1] == q[1]:
            p.popleft()
            q.popleft()
        p.popleft()      # remove one of the dulicates
        p.extendleft(q)  # merge
        p.append(p[0])   # complete the loop
        return p


class TwoColor(GraphSearch):
    __doc__ = f"""Implements depth-first search to determine if a graph is
    bipartite.
    {GraphSearch.__doc__}"""
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
    return max([G.degree(v) for v in G.vertices()])


def avg_degree(G):
    """Compute the theoretical average degree of the graph."""
    return 2 * G.E / G.V


def self_loops(G):
    """Return the number of self-loops in the graph."""
    s = 0
    for v in G.vertices():
        for w in G.adj(v):
            if v == w:
                s += 1
    return s // 2  # each edge counted twice


def dfs(G, s):
    """Search the graph from vertex `s`."""
    # See p 529
    search = DepthFirstSearch(G, s)
    for v in G.vertices():
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
    for v in G.vertices():
        print(f"{s:2d}->{v:2d}: ", end='')
        if search.has_path_to(v):
            for x in search.path_to(v):
                if x == s:
                    print(x, end='')
                else:
                    print(f"-{x}", end='')
        print()


def print_components(G):
    """Compute the connected components in the graph."""
    # See p 543
    cc = CC(G)
    M = cc.count()
    print(f"{M} components")
    components = [Bag() for _ in range(M)]
    for v in G.vertices():
        components[cc.id(v)].add(v)
    for i in range(M):
        print(f"{i}: ", end='')
        for v in components[i]:
            print(f"{v} ", end='')
        print()
    return components


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
        print(f"{source}->{sink}")
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
    # Graph = STGraph
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
    dfs(G, 0)
    print('----- DFS Paths -----')
    paths(G, 0, kind='DFS')
    print('----- BFS Paths -----')
    paths(G, 0, kind='BFS')

    # print('--- Cycle ---')
    G = Graph.fromfile(Path('../data/tinyG.txt'))
    c = CyclePath(G, 0)
    assert c.has_cycle
    assert list(c.cycle_path()) == [5, 4, 3, 5]

    G2 = Graph.fromfile(Path('../data/tinyG2.txt'))
    c2 = CyclePath(G2, 0)
    assert c2.has_cycle
    assert list(c2.cycle_path()) == [0, 6, 3, 2, 0]

    # Test connected components
    print('----- CC -----')
    comps = print_components(G2)
    print('--- subgraph 0 ---')
    G20 = G2.subgraph(comps[0])
    print(G20)

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
    assert ([bfs.dist_to(x) for x in G.vertices()]
            == [0, None, 1, 2, None, 1, 1, None, None, None, 2, None])

    # Test copy
    Gc = G.copy()
    for v in G.vertices():
        assert G.adj(v) == Gc.adj(v)
        assert G._adj[v] is not Gc._adj[v]

    # Test has_edge
    assert G.has_edge(0, 5)
    assert G.has_edge(8, 1)
    assert not G.has_edge(0, 8)

    # Test no parallel edges
    G2 = Graph.fromfile(Path('../data/tinyG2.txt'), parallel=False)
    G2.add_edge(0, 2)
    assert sorted(G2.adj(0)) == sorted(G.adj(0))  # no changes made
    G2.add_edge(0, 9)
    assert sorted(G2.adj(0)) != sorted(G.adj(0))  # changes made

    # Test no self-edges
    try:
        G.add_edge(9, 9)
    except ValueError:
        pass

    # Test UF search
    ufs = UFSearch(G, 0)
    assert all([ufs.marked(x) for x in [2, 3, 5, 6, 10]])
    assert ufs.count() == 6  # number of vertices in source component

    # Test leaf finding
    lfs = LeafDFS(G, 0)
    assert lfs.leaf() == 10

    # Test properties
    try:
        gp = GraphProperties(G)
    except ValueError:
        pass

    print('--- Graph Properties ---')
    # gc = Graph.fromfile(Path('../data/tinyCG.txt'))
    gc = Graph.fromfile(Path('../data/mediumG.txt'))
    # NOTE maximum recursion depth reached in largeG!
    # gc = Graph.fromfile(Path('../data/largeG.txt'), verbose=True)

    gp = GraphProperties(gc)
    print('eccentricity:', gp.eccentricity(0))
    print('    diameter:', gp.diameter())
    print('      radius:', gp.radius())
    print('      center:', gp.center())
    print('       girth:', gp.girth())
    assert gp.eccentricity(gp.center()) == gp.radius()

    c = MinCyclePath(gc, 0)
    print(c.cycle_path())

    for N in range(2, 10):
        edges = list()
        for i in range(N):
            edges.append((i, (i + 1) % N))
        Ncyc = Graph(N, edges)
        assert GraphProperties(Ncyc).girth() == N

    c = MinCyclePath(Ncyc, 0)
    print(c.cycle_path())

# =============================================================================
# =============================================================================
