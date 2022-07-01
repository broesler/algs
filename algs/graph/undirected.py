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

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from abc import ABC, abstractmethod
from collections import deque
from pathlib import Path
from tqdm import tqdm

from algs.basics import Bag, Stack, Queue
from algs.search import HashST, MultiHashSet
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
        if edges is None:
            edges = []
        try:
            for v, w in edges:
                self.add_edge(v, w)
        except ValueError:
            raise ValueError(f"{self.__class__.__name__} "
                             'expects an iterable of tuples.')

    @classmethod
    def fromfile(cls, filename, verbose=False, **kwargs):
        """Construct the graph structure from a file."""
        with open(Path(filename), 'r') as fp:
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
#         Graphs
# -----------------------------------------------------------------------------
class Graph(UndirectedGraph):
    __doc__ = f"""Implements a graph using an array of adjacency lists.
    {UndirectedGraph.__doc__}"""
    # See p 526

    def __init__(self, V=0, edges=None, parallel=True, self_loops=True):
        self._PARALLEL = bool(parallel)
        self._SELF_LOOPS = bool(self_loops)
        self._adj = [Bag() for _ in range(V)]
        super().__init__(V=V, edges=edges)

    __init__.__doc__ = f"""{UndirectedGraph.__init__.__doc__}
    parallel : bool, optional
        If True, allow parallel edges.
    self_loops : bool, optional
        If True, allow self-loops.
    """

    def _validate_vertex(self, v):
        if not (0 <= v < self.V):
            raise IndexError((f"Vertex index {v=} must be "
                              f"between 0 and {self.V=}!"))

    def vertices(self):
        return range(self.V)

    def adj(self, v):
        self._validate_vertex(v)
        return self._adj[v]

    def add_edge(self, v, w):
        self._validate_vertex(v)
        self._validate_vertex(w)
        # Exercise 4.1.5
        if not self._SELF_LOOPS and v == w:
            raise ValueError(f"{v} == {w}! No self-loops allowed.")
        if self._PARALLEL or not self.has_edge(v, w):
            self.E += 1
            self._adj[v].add(w)
            self._adj[w].add(v)

    # Exercise 4.1.25
    def _hide_vertex(self, v):
        """Hide the vertex from the graph."""
        self._validate_vertex(v)
        self._adj[v] = Bag()  # remove all edges so we don't include in paths

    # Exercise 4.1.3
    def copy(self):
        """Make a deep copy of the graph structure."""
        g = self.__class__(self.V)
        g.E = self.E
        for v in range(self.V):
            for w in self._adj[v]:
                g._adj[v].add(w)
        return g


class SimpleGraph(Graph):
    __doc__ = f"""Implements a graph using an array of adjacency lists, with no
    self-loops or parallel edges allowed.
    {UndirectedGraph.__doc__}"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, self_loops=False, parallel=False)


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

    @classmethod
    def fromadjfile(cls, filename, *args, delim=' ', verbose=False, **kwargs):
        """Construct an STGraph from a delimited text file containing an
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
        res : :obj:`STGraph`
            The STGraph defined by the adjaceny list file.
        """
        g = cls(*args, **kwargs)
        # One pass to add all vertices and edges to the symbol table
        with open(Path(filename), 'r') as fp:
            iters = fp.readlines()
            if verbose:
                iters = tqdm(iters)
            for line in iters:
                words = line.strip().split(delim)
                v = words[0]
                for w in words[1:]:
                    g.add_edge(v, w)
        return g

    __init__.__doc__ = f"""{UndirectedGraph.__init__.__doc__}
    self_loops : bool, optional
        If True, allow self-loops.
    """

    def _validate_vertex(self, v):
        if not self.has_vertex(v):
            raise IndexError(f"Vertex {v=} does not exist!")

    def has_vertex(self, v):
        return v in self._adj

    def vertices(self):
        return self._adj.keys()

    def adj(self, v):
        self._validate_vertex(v)
        return self._adj[v]

    def add_vertex(self, v):
        """Add a vertex to the graph."""
        if not self.has_vertex(v):
            self._adj[v] = Bag()
            self.V += 1

    def add_edge(self, v, w):
        if v not in self._adj:
            self.add_vertex(v)
        if w not in self._adj:
            self.add_vertex(w)
        # Exercise 4.1.5
        if not self._SELF_LOOPS and v == w:
            raise ValueError(f"{v} == {w}! No self-loops allowed.")
        if self._PARALLEL or not self.has_edge(v, w):
            self.E += 1
            self._adj[v].add(w)
            self._adj[w].add(v)

    # Exercise 4.1.3
    def copy(self):
        """Make a deep copy of the graph structure."""
        return self.subgraph(self.vertices())

    # Exercise 4.1.3 + 4.1.24
    def subgraph(self, vs):
        """Make a deep copy of the subgraph containing the vertices."""
        vs = set(vs)
        g = self.__class__(vs)
        for v in vs:
            for w in self._adj[v]:
                if w in vs:
                    g._adj[v].add(w)
        return g


class SymbolGraph:
    """Implements a symbol graph."""
    # See p 552

    def __init__(self, keys=None, edges=None, kind=Graph):
        self._st = HashST()  # map : str -> int
        self._keys = None    # map : int -> str
        self._GraphClass = kind
        self.G = None
        if keys is not None:
            for i, k in enumerate(keys):
                self._st[i] = k
            self._keys = keys
            self.G = self._GraphClass(V=len(keys), edges=edges)

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
        with open(Path(filename), 'r') as fp:
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
        sg.G = sg._GraphClass(V)
        with open(Path(filename), 'r') as fp:
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

    # Implement Graph methods with names as arguments
    def vertices(self):
        return [self.name(v) for v in self.G.vertices()]

    def adj(self, v):
        return [self.name(w) for w in self.G.adj(self.index(v))]

    def has_edge(self, v, w):
        return self.G.has_edge(self.index(v), self.index(w))

    def add_edge(self, v, w):
        return self.G.add_edge(self.index(v), self.index(w))


# Exercise 4.1.37
class EuclideanGraph(Graph):
    __doc__ = f"""Implements an undirected graph whose vertices are points in
    the plane with coordinates.
    {UndirectedGraph.__doc__}"""

    def __init__(self, G=None, x=None, y=None, *args, **kwargs):
        if G is None:
            super().__init__(*args, **kwargs)
        else:
            G = G.copy()
            self.V = G.V
            self.E = G.E
            self._adj = G._adj
            self._PARALLEL = G._PARALLEL
            self._SELF_LOOPS = G._SELF_LOOPS
        # Initialize coordinates
        if x is None:
            x = np.zeros(self.V)
        if y is None:
            y = np.zeros(self.V)
        if len(x) != self.V or len(y) != self.V:
            raise ValueError(f"Coordinates must have dimension {self.V=}")
        self.x = np.r_[x]
        self.y = np.r_[y]

    __init__.__doc__ = f"""{Graph.__init__.__doc__}
    x, y : (V,) arrays
        Cartesian coordinates for each vertex.
    """

    def set_coordinates(self, vs, xs, ys):
        """Set the coordinates of the vertices."""
        self.x[vs] = xs
        self.y[vs] = ys

    def get_coordinates(self, vs):
        """Get the coordinates of the vertices."""
        return np.c_[self.x[vs], self.y[vs]]

    def edges(self):
        """Return an iterable over the edges as pairs of vertices."""
        e = MultiHashSet()
        for v in self.vertices():
            for w in self.adj(v):
                # Only add single direction
                if (w, v) not in e:
                    e.append((v, w))
        return e

    def _draw_node(self, v, ax, label=None, **vkws):
        """Draw a single node."""
        fontcolor = vkws.get('fontcolor', 'k')
        edgecolor = vkws.get('edgecolor', 'k')
        fontsize = vkws.get('fontsize', 12)
        radius = vkws.get('radius', 0.02)
        circ = patches.Circle(
                (self.x[v], self.y[v]),
                radius=radius,
                edgecolor=edgecolor, facecolor='#EEE',
                zorder=3  # place on top of lines
                )
        ax.add_patch(circ)
        ax.annotate(label or v, xy=(self.x[v], self.y[v]),
                    color=fontcolor, fontsize=fontsize,
                    ha='center', va='center')

    def draw(self, p=None, ax=None, label_nodes=False, labels=None, c=None,
             vkws=None, ekws=None):
        """Plot the entire graph.

        Parameters
        ----------
        p : iterable of int
            Iterable of the vertices on the path from start to finish.
        ax : :obj:`plt.axes`
            The axes on which to plot. Uses current axes if None.
        label_nodes : bool
            If True, label the nodes with their indices.
        labels : dict
            Mapping from vertex IDs to strings for labelling nodes.
        c : color string
            Color to use for all edges and nodes.
        vkws, ekws : dict
            Vertex and edge keyword arguments to be passed to `ax.plot`.

        Returns
        -------
        ax : :obj:`plt.axes`
            The axes on which the graph was plotted.
        """
        _ekws = dict(ls='-', c='k', lw=2)
        _vkws = dict(s=100, c='k')
        if p is None:
            vs = self.vertices()
            es = self.edges()
        else:
            _vkws['edgecolor'] = 'k'
            p = list(p)
            vs = p
            es = [[p[i], p[i+1]] for i in range(len(p)-1)]

        if ax is None:
            ax = plt.gca()

        if c is not None:
            _ekws['c'] = c
            _vkws['c'] = c
            _vkws['edgecolor'] = c
            if label_nodes:
                _vkws['fontcolor'] = c

        # Set any user-defined parameters
        if vkws is not None:
            _vkws.update(vkws)
        if ekws is not None:
            _ekws.update(ekws)

        # Make the plot
        for e in es:
            ax.plot(self.x[list(e)], self.y[list(e)], **_ekws)

        # Plot the node itself
        if label_nodes:
            if labels is not None:
                for v in vs:
                    self._draw_node(v, ax, label=labels[v], **_vkws)
            else:
                for v in vs:
                    self._draw_node(v, ax, **_vkws)
        else:
            ax.scatter(self.x[vs], self.y[vs], **_vkws)

        ax.set_aspect('equal')
        ax.grid('off')
        ax.axis('off')  # hide everything but the grid
        return ax


class TransportationGraph(EuclideanGraph):
    __doc__ = f"""Implements an undirected graph whose vertices are points in
    the plane with coordinates. Also include a symbol table of paths denoting
    the "routes" in the transportation system.
    {UndirectedGraph.__doc__}"""

    def __init__(self, *args, routes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.routes = dict(routes)


# -----------------------------------------------------------------------------
#         Paths/Searches
# -----------------------------------------------------------------------------
class DepthFirstSearch(GraphSearch):
    __doc__ = f"""Implements depth-first search.
    {GraphSearch.__doc__}"""
    # See p 531

    def __init__(self, G, s):
        super().__init__(G, s)
        self._marked = G.V * [False]
        self._count = 0
        self._dfs(G, s)

    def marked(self, v):
        return self._marked[v]

    def count(self):
        return self._count

    def _dfs(self, G, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        self._count += 1
        for w in G.adj(v):
            if not self._marked[w]:
                self._dfs(G, w)


# Algorithm 4.1
class DepthFirstPaths(Paths):
    __doc__ = f"""Implements depth-first search to return a path.
    {Paths.__doc__}"""

    def __init__(self, G, s):
        super().__init__(G, s)
        self._marked = G.V * [False]
        self._edge_to = G.V * [None]  # last vertex on known path to this one
        self._dfs(G, s)

    def _dfs(self, G, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        for w in G.adj(v):
            if not self._marked[w]:
                self._edge_to[w] = v
                self._dfs(G, w)

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


class STDepthFirstPaths(DepthFirstPaths):
    __doc__ = f"""Implements depth-first search to return a path in an STGraph.
    {Paths.__doc__}"""

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
class DepthFirstPaths_nr(DepthFirstPaths):
    __doc__ = f"""Implements depth-first search non-recursively.

    .. note:: Extra memory includes a list of iterators over each adjacency
    list, plus the stack of vertices. Explores vertices in the same order as
    recursive DFS.
    {GraphSearch.__doc__}"""

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
class DepthFirstPaths_nr_simple(DepthFirstPaths):
    __doc__ = f"""Implements depth-first search non-recursively.

    .. note:: Extra memory is proportional to V + E, since each vertex may be
    pushed more than once. This implementation explores adjacent vertices in
    the opposite order of recursive DFS.
    {GraphSearch.__doc__}"""

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
class BreadthFirstPaths(Paths):
    __doc__ = f"""Implements breadth-first search to find shortest paths.
    {Paths.__doc__}"""

    def __init__(self, G, s):
        super().__init__(G, s)
        self._marked = G.V * [False]
        self._edge_to = G.V * [None]  # last vertex on known path to this one
        self._dist_to = G.V * [None]  # Exercise 4.1.13
        self._bfs(G, s)

    def _bfs(self, G, v):
        """Perform breadth-first search from vertex `v`."""
        q = Queue()
        self._marked[v] = True
        self._dist_to[v] = 0
        q.enqueue(v)
        while not q.is_empty:
            v = q.dequeue()
            for w in G.adj(v):
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
            for w in G.adj(v):
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
        self._leaf = self._dfs(G, s)

    def marked(self, v):
        return self._marked[v]

    def count(self):
        return self._count

    def _dfs(self, G, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        self._count += 1
        for w in G.adj(v):
            if not self._marked[w]:
                return self._dfs(G, w)
        return v  # return the leaf immediately when we find it

    def leaf(self):
        return self._leaf


# Web Exercise 33
def spanning_tree_dfs(G, s):
    """Return a Graph that is a spanning tree of `G`, rooted at `s`."""

    # Define the search to add edges to `T` as we traverse them.
    def _dfs(G, v):
        """Perform depth-first search from `v` with an explicit stack."""
        stack = Stack()
        adj = [iter(G.adj(v)) for v in G.vertices()]
        _marked[v] = True
        stack.push(v)
        while not stack.is_empty:
            v = stack.peek()
            try:
                w = next(adj[v])
                if not _marked[w]:
                    _marked[w] = True
                    T.add_edge(v, w)
                    stack.push(w)
            except StopIteration:
                stack.pop()

    # Define the tree with the same vertices as G
    T = Graph(G.V)
    _marked = G.V * [False]
    _dfs(G, s)
    return T


def spanning_tree_bfs(G, s):
    """Return a Graph that is a spanning tree of `G`, rooted at `s`."""

    # Define the search to add edges to `T` as we traverse them.
    def _bfs(G, v):
        """Perform breadth-first search from vertex `v`."""
        q = Queue()
        _marked[v] = True
        q.enqueue(v)
        while not q.is_empty:
            v = q.dequeue()
            for w in G.adj(v):
                if not _marked[w]:
                    _marked[w] = True
                    T.add_edge(v, w)
                    q.enqueue(w)

    # Define the tree with the same vertices as G
    T = Graph(G.V)
    _marked = G.V * [False]
    _bfs(G, s)
    return T


def spanning_forest_dfs(G):
    """Return a list of spanning trees for each connected component."""
    comps = CC(G).get_components()
    trees = list()
    for c in comps:
        trees.append(spanning_tree_dfs(G, c[0]))
    return trees


def spanning_forest_bfs(G):
    """Return a list of spanning trees for each connected component."""
    comps = CC(G).get_components()
    trees = list()
    for c in comps:
        trees.append(spanning_tree_bfs(G, c[0]))
    return trees


# -----------------------------------------------------------------------------
#         Graph Properties
# -----------------------------------------------------------------------------
# Exercise 4.1.16
class GraphProperties:
    """A class to determine the geometric properties of a connected graph.

    .. note:: The eccentricity of a single vertex is O(V²) since BFS is O(V+E),
        and we need to repeat for V vertices. The overall calculation is
        O(V³)(!!) since we need to compute the eccentricity of all V vertices
        to find the max and min.
    """

    def __init__(self, G, vertices=None, verbose=False):
        """
        Parameters
        ----------
        G : :obj:`Graph`
            The graph to analyze.
        vertices : iterable, optional
            An iterable of the vertices to consider. If not given, all vertices
            in `G` will be used.
        verbose : bool
            If True, show a progress bar.
        """
        if not CC_nr(G, vertices).is_connected:
            raise ValueError('Graph must be connected!')
        self.G = G
        self.vertices = list(vertices or self.G.vertices())
        self._VERBOSE = bool(verbose)
        # store in a symbol table (if vertices are not represented as integers)
        self._eccs = dict.fromkeys(self.vertices)
        self._dia = None
        self._rad = None
        self._girth = None

    def eccentricity(self, v):
        """The length of the shortest path from `v` to the furthest vertex from
        `v`, *i.e.* the maximum length of the shortest path to any vertex."""
        e = self._eccs[v]
        if e is None:
            e = self._ecc(v)
            self._eccs[v] = e
        return e

    def _ecc(self, v):
        """Compute the shortest path from `v` to every other vertex."""
        bfs = BreadthFirstPaths(self.G, v)
        return max([bfs.dist_to(w) for w in self.vertices])

    def _compute_missing_eccs(self):
        """Compute any missing eccentricity values."""
        if None in self._eccs.values():
            vs = [k for k, e in self._eccs.items() if e is None]
            if self._VERBOSE:
                vs = tqdm(vs)
            for v in vs:
                self._eccs[v] = self._ecc(v)

    def diameter(self):
        """The maximum eccentricity of any vertex."""
        self._compute_missing_eccs()
        self._dia = max(self._eccs.values())
        return self._dia

    def radius(self):
        """The smallest eccentricity of any vertex."""
        self._compute_missing_eccs()
        self._rad = min(self._eccs.values())
        return self._rad

    def center(self):
        """The set of vertices whose eccentricity is the radius."""
        self._compute_missing_eccs()
        if self._rad is None:
            self.radius()
        return [k for k, e in self._eccs.items() if e == self._rad]

    def periphery(self):
        """The set of vertices whose eccentricity is the diameter."""
        self._compute_missing_eccs()
        if self._dia is None:
            self.diameter()
        return [k for k, e in self._eccs.items() if e == self._dia]

    def girth(self):
        """Return the length of the shortest cycle in the graph.
        If there are no cycles, the girth is infinite.

        .. note:: This algorithm runs in O(V(V + E)) time, since all source
            vertices must be checked, and BFS runs in O(V + E) worst-case time.
            This runtime improves over O(E(V + E)), since E ∈ [V-1, (V-1)V/2].

        .. note:: Example of graph where BFS would *not* find the minimum cycle
            in a connected graph just by searching from one vertex:
        >>> G = Graph.fromfile('../data/tinyG2.txt')
        >>> cc = CC(G).get_components()
        >>> print(cc[0])
        [0, 2, 3, 5, 6, 10]
        >>> list(MinCyclePath(G,  0).cycle())
        [2, 0, 6, 2]
        >>> list(MinCyclePath(G, 10).cycle())
        [2, 3, 10, 5, 2]

        Lengths are not equal! The minimum path in that group is 3.
        """
        if self._girth is not None:
            return self._girth

        # G is guaranteed to be connected, so only need to check one vertex
        m = float('inf')  # set "minimum" to maximum
        if not Cycle_nr(self.G, self.vertices[0]).has_cycle:
            self._girth = m
            return m

        # Compute the shortest cycle: O(V(V + E))
        vs = tqdm(self.vertices) if self._VERBOSE else self.vertices
        for v in vs:
            bfs = MinCyclePath(self.G, v)
            m = min(m, bfs.cycle_length)
            if m == 3:
                break  # no possible shorter cycle

        self._girth = m
        return m


# Algorithm 4.3
class CC:
    """Implements a depth-first search to find connected components.

    Attributes
    ----------
    G : :obj:`Graph`
        The graph to analyze.
    """

    def __init__(self, G, vertices=None):
        """
        Parameters
        ----------
        G : :obj:`Graph`
            The graph to analyze.
        vertices : iterable, optional
            An iterable of the vertices to consider. If not given, all vertices
            in `G` will be used. The order of the iterable is preserved.
        """
        if vertices is None:
            vertices = G.vertices()
        self._vs = vertices
        self._marked = G.V * [False]
        self._id = G.V * [None]
        self._count = 0
        # Perform DFS for *every* source vertex.
        for s in self._vs:
            if not self._marked[s]:
                self._dfs(G, s)
                self._count += 1

    def _dfs(self, G, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        self._id[v] = self._count
        for w in G.adj(v):
            if not self._marked[w]:
                self._dfs(G, w)

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

    @property
    def is_connected(self):
        return self._count == 1

    def get_components(self):
        """Return a list of lists of vertices in each component."""
        components = [list() for _ in range(self._count)]
        for v in self._vs:
            components[self._id[v]].append(v)
        return components


class CC_nr(CC):
    """Implements a depth-first search to find connected components,
    non-recursively.

    Attributes
    ----------
    G : :obj:`Graph`
        The graph to analyze.
    """

    def _dfs(self, G, v):
        """Perform depth-first search non-recursively from vertex `v`."""
        stack = Stack()
        adj = [iter(G.adj(v)) for v in G.vertices()]
        self._marked[v] = True
        self._id[v] = self._count
        stack.push(v)
        while not stack.is_empty:
            v = stack.peek()
            try:
                w = next(adj[v])
                if not self._marked[w]:
                    self._marked[w] = True
                    self._id[w] = self._count
                    stack.push(w)
            except StopIteration:
                stack.pop()


class Cycle:
    __doc__ = f"""Implements depth-first search to find a cycle.
    {GraphSearch.__doc__}"""
    # See p 547

    def __init__(self, G, s):
        self.s = s
        self.has_cycle = False
        # Don't actually check for undirected graphs. See method note.
        # if self.has_parallel_edges(G):
        #     return
        self._marked = G.V * [False]
        self._dfs(G, s, s)

    @staticmethod
    def has_self_loop(G):
        """Return True if the graph has a self-loop."""
        for v in G.vertices():
            for w in G.adj(v):
                if v == w:
                    return True
        else:
            return False

    @staticmethod
    def has_parallel_edges(G):
        """Return True if the graph has parallel edges."""
        # Only return True if G.adj(v) has duplicates
        for v in G.vertices():
            adj = sorted(G.adj(v))
            for i in range(len(adj)-1):
                if adj[i] == adj[i+1]:
                    return True
        return False

    def _dfs(self, G, v, u):
        """Perform depth-first search recursively from vertex `v`.

        .. note:: `u` is the previously-seen vertex. If one of the adjacent
            vertices to `v` is marked, but is not the vertex from which we just
            came, we have a cycle.
        """
        self._marked[v] = True
        for w in G.adj(v):
            if self.has_cycle:
                return
            if not self._marked[w]:
                self._dfs(G, w, v)
            elif w != u:
                self.has_cycle = True


class Cycle_nr(Cycle):
    __doc__ = f"""Implements depth-first search to find a cycle.
    {GraphSearch.__doc__}"""
    # See p 547

    def _dfs(self, G, v, u):
        """Perform depth-first search non-recursively from vertex `v`.

        .. note:: `u` is the previously-seen vertex. If one of the adjacent
            vertices to `v` is marked, but is not the vertex from which we just
            came, we have a cycle.
        """
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
                    u = v
                    stack.push(w)
                elif w != u:
                    self.has_cycle = True
                    return
            except StopIteration:
                stack.pop()


class CyclePath(DepthFirstPaths):
    __doc__ = f"""Implements depth-first search to find a cyclic path.
    {GraphSearch.__doc__}"""

    def __init__(self, G, s):
        self.s = s
        self.has_cycle = False
        self._path = None
        self._marked = G.V * [False]
        self._edge_to = G.V * [None]  # last vertex on known path to this one
        self._cycle_head = None  # start vertex of the cycle
        self._cycle_tail = None  # end vertex of the cycle
        self._dfs(G, s, s)

    def _dfs(self, G, v, u):
        """Perform depth-first search recursively from vertex `v`.

        .. note:: `u` is the previously-seen vertex. If one of the adjacent
            vertices to `v` is marked, but is not the vertex from which we just
            came, we have a cycle.
        """
        self._marked[v] = True
        for w in G.adj(v):
            if self.has_cycle:
                return
            if not self._marked[w]:
                self._edge_to[w] = v
                self._dfs(G, w, v)
            elif w != u:
                self.has_cycle = True
                self._path = Stack()
                x = v
                while x != w:
                    self._path.push(x)
                    x = self._edge_to[x]
                self._path.push(w)
                self._path.push(v)

    def cycle(self):
        """Return the path of the found cycle."""
        return list(self._path)


class CyclePath_nr(CyclePath):
    __doc__ = f"""Implements depth-first search to find a cyclic path.
    {GraphSearch.__doc__}"""

    def _dfs(self, G, v, u):
        """Perform depth-first search non-recursively from vertex `v`.

        .. note:: `u` is the previously-seen vertex. If one of the adjacent
            vertices to `v` is marked, but is not the vertex from which we just
            came, we have a cycle.
        """
        stack = Stack()
        adj = [iter(G.adj(v)) for v in G.vertices()]
        self._marked[v] = True
        stack.push(v)
        while not stack.is_empty:
            v = stack.peek()
            try:
                w = next(adj[v])
                if not self._marked[w]:
                    self._edge_to[w] = v
                    u = v
                    self._marked[w] = True
                    stack.push(w)
                elif w != u:
                    self.has_cycle = True
                    self._path = Stack()
                    x = v
                    while x != w:
                        self._path.push(x)
                        x = self._edge_to[x]
                    self._path.push(w)
                    self._path.push(v)
                    return
            except StopIteration:
                stack.pop()


class MinCyclePath(BreadthFirstPaths):
    __doc__ = f"""Implements breadth-first search to find a minimum cycle.
    {GraphSearch.__doc__}"""

    def __init__(self, G, s):
        self.s = s
        self.has_cycle = False
        self.cycle_length = float('inf')
        self._marked = G.V * [False]
        self._edge_to = G.V * [None]
        self._dist_to = G.V * [None]
        self._cycle_head = None  # start vertex of the cycle
        self._cycle_tail = None  # end vertex of the cycle
        # Run the search
        self._bfs(G, s)

    def _bfs(self, G, v):
        """Perform breadth-first search from vertex `v`."""
        q = Queue()
        self._marked[v] = True
        self._dist_to[v] = 0
        q.enqueue(v)
        while not q.is_empty:
            v = q.dequeue()
            for w in G.adj(v):
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

    def cycle(self):
        """Return the path of the found cycle."""
        # BFS gives two paths: one each from the source to the head and tail.
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
        return list(p)


class Bipartite:
    __doc__ = f"""Implements depth-first search to determine if a graph is
    bipartite.
    {GraphSearch.__doc__}"""
    # See p 547

    def __init__(self, G, s):
        self.s = s
        self._marked = G.V * [False]
        self._color = G.V * [False]
        self.is_bipartite = True
        self._dfs(G, s)

    def _dfs(self, G, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        for w in G.adj(v):
            if not self._marked[w]:
                self._color[w] = not self._color[v]
                self._dfs(G, w)
            elif self._color[w] == self._color[v]:
                self.is_bipartite = False


# Exercise 4.1.32
class ParallelEdges:
    __doc__ = f"""Implements breadth-first search to count parallel edges.
    {Paths.__doc__}"""

    def __init__(self, G, s):
        self.count = 0
        self._marked = G.V * [False]
        self._bfs(G, s)
        self.count /= 2  # undirected edges counted 2x

    def _bfs(self, G, s):
        """Perform breadth-first search from source vertex `s`."""
        q = Queue()
        self._marked[s] = True
        q.enqueue(s)
        while not q.is_empty:
            v = q.dequeue()
            neighbs = G.V * [False]  # boolean array of (possible) neighbors
            for w in G.adj(v):
                # Same as using a hash table since we have integer vertices.
                if neighbs[w]:
                    self.count += 1
                else:
                    neighbs[w] = True

                if not self._marked[w]:
                    self._marked[w] = True
                    q.enqueue(w)


# Exercise 4.1.36
class Biconnected:
    __doc__ = f"""Implements depth-first search to determine if a graph is
    edge-connected, aka biconnected.
    {GraphSearch.__doc__}"""

    def __init__(self, G):
        self.Nbridges = 0
        self._count = 0           # depth counter
        self._pre = G.V * [None]  # order in which DFS examines v
        self._low = G.V * [None]  # lowest preorder of any vertex adjacent to v
        self._art = G.V * [False]  # is the vertex an articulation point?
        for s in G.vertices():
            if self._pre[s] is None:
                self._dfs(G, s, s)

    @property
    def is_edge_connected(self):
        return self.Nbridges == 0

    def _dfs(self, G, v, u):
        """Perform depth-first search recursively from vertex `v`.

        .. note:: `u` is the previously-seen vertex. If one of the adjacent
            vertices to `v` is marked, but is not the vertex from which we just
            came, we have a cycle.
        """
        children = 0
        self._pre[v] = self._count
        self._low[v] = self._pre[v]
        self._count += 1
        for w in G.adj(v):
            # "pre is None" takes the place of "not marked"
            if self._pre[w] is None:
                children += 1
                self._dfs(G, w, v)
                self._low[v] = min(self._low[v], self._low[w])
                # Check if edge_to[w] is a bridge
                if self._low[w] == self._pre[w]:
                    self.Nbridges += 1
                # Check if non-root is an articulation point
                if self._low[w] >= self._pre[v] and u != v:
                    self._art[w] = True
            elif w != u:
                # Update low number -- ignore reverse of edge leading to v
                self._low[v] = min(self._low[v], self._pre[w])
        # root is an articulation point if it has multiple children
        if u == v and children > 1:
            self._art[v] = True

    def articulation(self, v):
        """Return True if `v` is an articulation point."""
        return self._art[v]


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


def print_dfs(G, s, DFS=DepthFirstSearch):
    """Search the graph from vertex `s`."""
    # See p 529
    search = DFS(G, s)
    for v in G.vertices():
        if search.marked(v):
            print(f"{v} ", end='')
    print()
    if search.count() != G.V:
        print('NOT ', end='')
    print('connected.')
    return search


def print_paths(G, s, GS=DepthFirstPaths):
    """Search the graph from vertex `s`, returning the paths."""
    # See p 535
    search = GS(G, s)
    for v in G.vertices():
        print(f"{s:2d}->{v:2d}: ", end='')
        if search.has_path_to(v):
            for x in search.path_to(v):
                if x == s:
                    print(x, end='')
                else:
                    print(f"-{x}", end='')
        print()


def print_components(G, vertices=None):
    """Compute the connected components in the graph.

    Parameters
    ----------
    G : :obj:`Graph`
        The graph to analyze.
    vertices : iterable, optional
        An iterable of the vertices to consider. If not given, all vertices
        in `G` will be used.

    Returns
    -------
    components : list of lists
        List of lists of the vertices in each connected component.
    """
    # See p 543
    vertices = vertices or G.vertices()
    cc = CC(G, vertices)
    M = cc.count()
    print(f"{M} components")
    components = cc.get_components()
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
    for w in sg.adj(s):
        print(' ', w)


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


if __name__ == "__main__":
    G = Graph.fromfile('../data/tinyG.txt')
    G2 = Graph.fromfile('../data/tinyG2.txt')

    print('----- DFS -----')
    print_dfs(G, 0)
    print_dfs(G, 9)

    # Test paths
    print('----- Connected Graph -----')
    GC = Graph.fromfile('../data/tinyCG.txt')
    print(GC)
    print_dfs(GC, 0)

    print('----- DFS Paths -----')
    print_paths(GC, 0, GS=DepthFirstPaths)

    print('----- BFS Paths -----')
    print_paths(GC, 0, GS=BreadthFirstPaths)

    # Test connected components
    print('----- CC -----')
    comps = print_components(G2)
    comps20 = print_components(G2, vertices=comps[0])

    # Test connected components
    print('----- SymbolGraph -----')
    sg = SymbolGraph.fromfile('../data/routes.txt')
    print('--- adjacency lists ---')
    print_adj(sg, 'JFK')
    print_adj(sg, 'LAX')
    print('--- shortest paths ---')
    degrees_of_separation(sg, 'JFK', 'LAS')
    degrees_of_separation(sg, 'JFK', 'DFW')

    # sg = SymbolGraph.fromfile('../data/movies.txt', delim='/')
    # print('--- adjacency lists ---')
    # print_adj(sg, 'Top Gun (1986)')
    # print('--- shortest paths ---')
    # degrees_of_separation(sg, 'Animal House (1978)', 'Titanic (1997)')
    # degrees_of_separation(sg, 'Bacon, Kevin', 'Cruise, Tom')

    print('----- Graph Properties of mediumG -----')
    Gm = Graph.fromfile('../data/mediumG.txt')
    # NOTE maximum recursion depth reached in largeG!
    # gc = Graph.fromfile('../data/largeG.txt', verbose=True)

    gp = GraphProperties(Gm)
    print('        ϵ:', gp.eccentricity(0))
    print(' diameter:', gp.diameter())
    print('   radius:', gp.radius())
    print('   center:', gp.center())
    print('periphery:', gp.periphery())
    print('    girth:', gp.girth())
    assert gp.eccentricity(gp.center()[0]) == gp.radius()

    print('--- MinCyclePath ---')
    cp = CyclePath(Gm, 0)
    print('   path', cp.cycle())
    cm = MinCyclePath(Gm, 0)
    print('minpath', cm.cycle())

# =============================================================================
# =============================================================================
