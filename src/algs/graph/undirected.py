#!/usr/bin/env python3
# =============================================================================
#     File: undirected.py
#  Created: 2022-06-14 21:05
#   Author: Bernie Roesler
# =============================================================================

"""
Implementations of undirected graph representations and associated algorithms.

See Sedgewick and Wayne, §4.1.
"""

from abc import ABC, abstractmethod
from collections import deque, namedtuple
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from tqdm import tqdm

from algs import WeightedQuickUnionUF
from algs.basics import Bag, Queue, Stack
from algs.search import HashST, MultiHashSet


# -----------------------------------------------------------------------------
#         Abstract Base Classes
# -----------------------------------------------------------------------------
class BaseGraph(ABC):
    # An abstract base class implementing the Graph API. See p 522.
    """
    Attributes
    ----------
    V : int
        number of vertices
    E : int
        number of edges
    """

    def __init__(self, V=0, edges=None, parallel=True, self_loops=True):
        self._V = V
        self._E = 0
        self._parallel = bool(parallel)
        self._self_loops = bool(self_loops)
        self._adj = self._create_adjacency_structure(V)

        if edges is None:
            edges = []

        try:
            for v, w in edges:
                self.add_edge(v, w)
        except ValueError:
            raise ValueError(
                f"{self.__class__.__name__} expects `edges`"
                "to be an iterable of tuples."
            )

    def _create_adjacency_structure(self, V):
        """Create the underlying adjacency structure for the graph. This is
        a factory method that should be overridden by subclasses.
        """
        if not isinstance(V, int):
            raise ValueError(f"Number of vertices must be an integer! Got {type(V)=}.")

        if V < 0:
            raise ValueError(f"Number of vertices {V=} must be > 0!")

        return [Bag() for _ in range(V)]

    @property
    def V(self):
        """Return the number of vertices."""
        return self._V

    @property
    def E(self):
        """Return the number of edges."""
        return self._E

    @classmethod
    def fromfile(cls, filename, verbose=False, **kwargs):
        """Construct the graph structure from a file."""
        with Path(filename).open() as fp:
            V = int(fp.readline())
            E = int(fp.readline())
            G = cls(V=V, **kwargs)
            for line in tqdm(fp.readlines(), disable=not verbose):
                v, w = line.strip().split()
                G.add_edge(int(v), int(w))
            assert E == G.E
            return G

    @abstractmethod
    def add_edge(self, v, w):
        """Add an edge from `v` to `w`."""
        pass

    def adj(self, v):
        """Return an iterable of vertices adjacent to `v`."""
        self._validate_vertex(v)
        return self._adj[v]

    def degree(self, v):
        """Return the degree of vertex `v`."""
        return len(self.adj(v))

    # Exercise 4.1.4, 4.2.4
    def has_edge(self, v, w):
        """Return True if an edge from `v` to `w` exists."""
        return w in self.adj(v)

    def vertices(self):
        """Return an iterable over the vertices."""
        return range(self._V)

    def _validate_vertex(self, v):
        if not (0 <= v < self.V):
            raise IndexError(f"Vertex index {v=} must be between 0 and {self._V=}!")

    def __str__(self):
        s = f"{self._V} vertices, {self._E} edges\n"
        for v in self.vertices():
            s += f"{v}: " + ' '.join(str(w) for w in self.adj(v)) + '\n'
        return s.strip()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"


def _reconstruct_path(v, s, edge_to):
    """Reconstruct the list of vertices on the path from `v` to `s` using the
    `edge_to` array.
    """
    path = Stack()
    x = v
    while x != s:
        path.push(x)
        x = edge_to[x]
    path.push(s)
    return path


_SEARCH_DOC = """
Attributes
----------
s : int
    The index of the source vertex.
"""


class GraphSearch(ABC):
    """An abstract base class for implementing graph search algorithms.

    This class should not be instantiated, because it does not actually do
    anything. A subclass should call `super().__init__(G, s)` to initialize the
    search structure, and then implement the search itself, which should
    populate the `_marked` and `_edge_to` attributes. The `has_path_to` and
    `path_to` methods will then work as expected.
    """

    @abstractmethod
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
        self._marked = G.V * [False]
        self._edge_to = G.V * [None]  # last vertex on known path to this one

    @property
    def count(self):
        """Return the number of vertices connected to `s`."""
        return sum(self._marked)

    def has_path_to(self, v):
        """Return True if there is a path from `s` to `v`."""
        return self._marked[v]

    def path_to(self, v):
        """Return an iterable of the vertices on the path from `s` to `v`."""
        return (
            _reconstruct_path(v, self.s, self._edge_to) if self.has_path_to(v) else None
        )


# -----------------------------------------------------------------------------
#         Graphs
# -----------------------------------------------------------------------------
class Graph(BaseGraph):
    __doc__ = f"""Implements a graph using an array of adjacency lists.
    {BaseGraph.__doc__}"""
    # See p 526

    def add_edge(self, v, w):
        """Add an edge from `v` to `w`."""
        self._validate_vertex(v)
        self._validate_vertex(w)
        # Exercise 4.1.5
        if not self._self_loops and v == w:
            raise ValueError(f"{v} == {w}! No self-loops allowed.")
        if self._parallel or not self.has_edge(v, w):
            self._E += 1
            self._adj[v].add(w)
            self._adj[w].add(v)

    # Exercise 4.1.25
    def _hide_vertex(self, v):
        """Hide the vertex from the graph."""
        self._validate_vertex(v)
        self._adj[v] = Bag()  # remove all edges so we don't include in paths

    # Exercise 4.1.3, 4.2.3
    def copy(self):
        """Make a deep copy of the graph structure."""
        g = self.__class__(self._V)
        g._E = self._E
        for v in range(self._V):
            for w in self._adj[v]:
                g._adj[v].add(w)
        return g


class SimpleGraph(Graph):
    __doc__ = f"""Implements a graph using an array of adjacency lists, with no
    self-loops or parallel edges allowed.
    {BaseGraph.__doc__}"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, self_loops=False, parallel=False)


class STGraph(BaseGraph):
    __doc__ = f"""Implements a graph using a symbol table of adjacency lists.
    {BaseGraph.__doc__}"""
    # See p 557 and
    # <https://introcs.cs.princeton.edu/java/45graph/Graph.java.html>

    def _create_adjacency_structure(self, V):
        """Create the underlying adjacency structure for the graph. This is
        a factory method that should be overridden by subclasses.
        """
        self._adj = HashST()
        self._V = 0

        if V is None:
            return self._adj

        if isinstance(V, int):
            if V < 0:
                raise ValueError(f"Number of vertices {V=} must be > 0!")

            # If V is an integer, number the vertices accordingly
            for v in range(V):
                self.add_vertex(v)
        else:
            try:
                for v in V:
                    self.add_vertex(v)
            except TypeError:
                raise ValueError(f"Vertices must be an iterable! Got {type(V)=}.")

        return self._adj

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
        with Path(filename).open() as fp:
            for line in tqdm(fp.readlines(), disable=not verbose):
                words = line.strip().split(delim)
                v = words[0]
                for w in words[1:]:
                    g.add_edge(v, w)
        return g

    def _validate_vertex(self, v):
        if not self.has_vertex(v):
            raise IndexError(f"Vertex {v=} does not exist!")

    def has_vertex(self, v):
        """Return True if `v` is a vertex in the graph."""
        return v in self._adj

    def vertices(self):
        """Return an iterable over the vertices."""
        return self._adj.keys()

    def add_vertex(self, v):
        """Add a vertex to the graph."""
        if not self.has_vertex(v):
            self._adj[v] = Bag()
            self._V += 1

    def add_edge(self, v, w):
        """Add an edge from `v` to `w`."""
        if v not in self._adj:
            self.add_vertex(v)
        if w not in self._adj:
            self.add_vertex(w)
        # Exercise 4.1.5
        if not self._self_loops and v == w:
            raise ValueError(f"{v} == {w}! No self-loops allowed.")
        if self._parallel or not self.has_edge(v, w):
            self._E += 1
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
        self._keys = None  # map : int -> str
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
        with Path(filename).open() as fp:
            for line in tqdm(fp.readlines(), disable=not verbose):
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
        with Path(filename).open() as fp:
            for line in fp.readlines():
                words = line.strip().split(delim)
                v = sg._st[words[0]]
                for w in words[1:]:
                    sg.G.add_edge(v, sg._st[w])

        return sg

    @property
    def V(self):
        """Return the number of vertices."""
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
        """Return True if `k` is a vertex."""
        return self.__contains__(k)

    # Implement Graph methods with names as arguments
    def vertices(self):
        """Return an iterable over the vertices."""
        return [self.name(v) for v in self.G.vertices()]

    def adj(self, v):
        """Return an iterable of vertices adjacent to `v`."""
        return [self.name(w) for w in self.G.adj(self.index(v))]

    def has_edge(self, v, w):
        """Return True if an edge from `v` to `w` exists."""
        return self.G.has_edge(self.index(v), self.index(w))

    def add_edge(self, v, w):
        """Add an edge from `v` to `w`."""
        return self.G.add_edge(self.index(v), self.index(w))


# Exercise 4.1.37
class EuclideanGraph(Graph):
    __doc__ = f"""Implements an undirected graph whose vertices are points in
    the plane with coordinates.
    {BaseGraph.__doc__}"""

    def __init__(self, G=None, x=None, y=None, two_color=False, *args, **kwargs):
        if G is None:
            super().__init__(*args, **kwargs)
        else:
            G = G.copy()
            self._V = G.V
            self._E = G.E
            self._adj = G._adj
            self._parallel = G._parallel
            self._self_loops = G._self_loops
        # Initialize coordinates
        if x is None:
            x = np.zeros(self._V)
        if y is None:
            y = np.zeros(self._V)
        if len(x) != self._V or len(y) != self._V:
            raise ValueError(f"Coordinates must have dimension {self._V=}")
        self.x = np.r_[x]
        self.y = np.r_[y]
        self._TWO_COLOR = bool(two_color)
        self._node_colors = None

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
                    e.add((v, w))
        return e

    def _draw_node(self, v, ax, label=None, **vkws):
        """Draw a single node."""
        # Better way get these kwargs?
        fc_default = self._node_colors[v] if self._TWO_COLOR else 'k'
        ec_default = self._node_colors[v] if self._TWO_COLOR else 'k'
        fontcolor = vkws.get('fontcolor', fc_default)
        edgecolor = vkws.get('edgecolor', ec_default)
        fontsize = vkws.get('fontsize', 12)
        radius = vkws.get('radius', 0.02)
        # Create the node
        circ = patches.Circle(
            (self.x[v], self.y[v]),
            radius=radius,
            edgecolor=edgecolor,
            facecolor='#EEE',
            zorder=3,  # place on top of lines
        )
        # Add it to the axes
        ax.add_patch(circ)
        ax.annotate(
            label or v,
            xy=(self.x[v], self.y[v]),
            color=fontcolor,
            fontsize=fontsize,
            ha='center',
            va='center',
        )

    def draw(
        self,
        p=None,
        ax=None,
        label_nodes=False,
        labels=None,
        c=None,
        vkws=None,
        ekws=None,
    ):
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
        _ekws = {"ls": '-', "c": 'k', "lw": 1}
        _vkws = {"s": 10, "c": 'k'}
        if p is None:
            vs = self.vertices()
            es = self.edges()
        else:
            _vkws['edgecolor'] = 'k'
            p = list(p)
            vs = p
            es = [[p[i], p[i + 1]] for i in range(len(p) - 1)]

        if ax is None:
            ax = plt.gca()

        if c is not None:
            _ekws['c'] = c
            _vkws['c'] = c
            _vkws['edgecolor'] = c
            if label_nodes:
                _vkws['fontcolor'] = c

        if self._TWO_COLOR:
            bp = bipartite_colors(self)
            if bp.colors is not None:
                self._node_colors = np.where(bp.colors, 'tab:red', 'k')
            else:
                self._node_colors = np.full(self._V, 'k')

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
    {BaseGraph.__doc__}"""

    def __init__(self, *args, routes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.routes = dict(routes)


# -----------------------------------------------------------------------------
#         Paths/Searches
# -----------------------------------------------------------------------------
# See: Algorithm 4.1 DepthFirstPaths (p 536) + DepthFirstSearch (p 531)
class DepthFirstSearch(GraphSearch):
    __doc__ = f"""Implements depth-first search to return a path.
    {_SEARCH_DOC}"""

    def __init__(self, G, s):
        super().__init__(G, s)
        self._dfs(G, s)

    def _dfs(self, G, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        for w in G.adj(v):
            if not self._marked[w]:
                self._edge_to[w] = v
                self._dfs(G, w)


class STDepthFirstPaths(DepthFirstSearch):
    __doc__ = f"""Implements depth-first search to return a path in an STGraph.
    {_SEARCH_DOC}"""

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
    __doc__ = f"""Implements depth-first search non-recursively.

    .. note:: Extra memory includes a list of iterators over each adjacency
    list, plus the stack of vertices. Explores vertices in the same order as
    recursive DFS.
    {_SEARCH_DOC}"""

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
    __doc__ = f"""Implements depth-first search non-recursively.

    .. note:: Extra memory is proportional to V + E, since each vertex may be
    pushed more than once. This implementation explores adjacent vertices in
    the opposite order of recursive DFS.
    {_SEARCH_DOC}"""

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
    __doc__ = f"""Implements breadth-first search to find shortest paths.
    {_SEARCH_DOC}"""

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
    __doc__ = f"""Implements the graph search API using Union-Find.

    .. note:: This implementation is simple and efficient if we are only
        concerned with determining connectivity. The UF algorithm is also an
        *online* algorithm, as opposed to DFS which must preprocess the entire
        graph structure.
    {_SEARCH_DOC}"""
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
        """Return the number of vertices connected to `s`.

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
    __doc__ = f"""Implements depth-first search to find a non-structural
    vertex, aka a leaf of a spanning tree rooted at the source.
    {_SEARCH_DOC}"""

    def __init__(self, G, s):
        super().__init__(G, s)
        self._leaf = self._dfs(G, s)

    @property
    def leaf(self):
        """Return the leaf vertex found by the search."""
        return self._leaf

    def _dfs(self, G, v):
        """Perform depth-first search recursively from vertex `v`."""
        self._marked[v] = True
        for w in G.adj(v):
            if not self._marked[w]:
                return self._dfs(G, w)
        return v  # return the leaf immediately when we find it


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
    trees = []
    for c in comps:
        trees.append(spanning_tree_dfs(G, c[0]))
    return trees


def spanning_forest_bfs(G):
    """Return a list of spanning trees for each connected component."""
    comps = CC(G).get_components()
    trees = []
    for c in comps:
        trees.append(spanning_tree_bfs(G, c[0]))
    return trees


# Web Exercise 31
def complement_graph(G):
    """Return a Graph that has an edge v-w iff v-w is not in `G`."""
    Gc = Graph(G.V)
    vs = set(range(G.V))
    for v in range(G.V):
        Gc._adj[v] = Bag(vs - set([v] + list(G.adj(v))))
    return Gc


# See:
# <https://stackoverflow.com/questions/24476027/shortest-path-in-a-complement-graph-algorithm>
class ComplementBFS(GraphSearch):
    __doc__ = f"""Implements breadth-first search to find shortest paths in the
    complement graph.
    {_SEARCH_DOC}"""

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
        """Return the length of the shortest path from `v` to the furthest
        vertex from `v`, *i.e.* the maximum length of the shortest path to any
        vertex.
        """
        e = self._eccs[v]
        if e is None:
            e = self._ecc(v)
            self._eccs[v] = e
        return e

    def _ecc(self, v):
        """Compute the shortest path from `v` to every other vertex."""
        bfs = BreadthFirstSearch(self.G, v)
        return max([bfs.dist_to(w) for w in self.vertices])

    def _compute_missing_eccs(self):
        """Compute any missing eccentricity values."""
        if None in self._eccs.values():
            vs = [k for k, e in self._eccs.items() if e is None]
            for v in tqdm(vs, disable=not self._VERBOSE):
                self._eccs[v] = self._ecc(v)

    def diameter(self):
        """Return the maximum eccentricity of any vertex."""
        self._compute_missing_eccs()
        self._dia = max(self._eccs.values())
        return self._dia

    def radius(self):
        """Return the smallest eccentricity of any vertex."""
        self._compute_missing_eccs()
        self._rad = min(self._eccs.values())
        return self._rad

    def center(self):
        """Return the set of vertices whose eccentricity is the radius."""
        self._compute_missing_eccs()
        if self._rad is None:
            self.radius()
        return [k for k, e in self._eccs.items() if e == self._rad]

    def periphery(self):
        """Return the set of vertices whose eccentricity is the diameter."""
        self._compute_missing_eccs()
        if self._dia is None:
            self.diameter()
        return [k for k, e in self._eccs.items() if e == self._dia]

    # Exercise 4.1.18
    def girth(self):
        """Return the length of the shortest cycle in the graph.
        If there are no cycles, the girth is infinite.

        .. note:: This algorithm runs in O(V(V + E)) time, since all source
            vertices must be checked, and BFS runs in O(V + E) worst-case time.
            This runtime improves over O(E(V + E)), since E ∈ [V-1, (V-1)V/2].

        .. note:: Example of graph where BFS would *not* find the minimum cycle
            in a connected graph just by searching from one vertex:
        >>> G = Graph.fromfile(DATA_PATH / 'tinyG2.txt')
        >>> cc = CC(G).get_components()
        >>> print(cc[0])
        [0, 2, 3, 5, 6, 10]
        >>> list(find_min_cycle(G,  0))
        [2, 0, 6, 2]
        >>> list(find_min_cycle(G, 10))
        [2, 3, 10, 5, 2]

        Lengths are not equal! The minimum path in that group is 3.
        """
        if self._girth is not None:
            return self._girth

        m = float('inf')  # set "minimum" to maximum

        # G is guaranteed to be connected, so only need to check one vertex
        if not has_cycle(self.G, self.vertices[0]):
            self._girth = m
            return m

        # Compute the shortest cycle: O(V(V + E))
        for v in tqdm(self.vertices, disable=not self._VERBOSE):
            min_cycle = find_min_cycle(self.G, v)
            m = min(m, (len(min_cycle) - 1) if min_cycle else float('inf'))
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
        """Return the number of connected components."""
        return self._count

    @property
    def is_connected(self):
        """Return True if the graph is connected."""
        return self._count == 1

    def get_components(self):
        """Return a list of lists of vertices in each component."""
        components = [[] for _ in range(self._count)]
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


def has_self_loop(G):
    """Return True if the graph has a self-loop."""
    for v in G.vertices():
        for w in G.adj(v):
            if v == w:
                return True
    return False


def has_parallel_edges(G):
    """Return True if the graph has parallel edges."""
    # Only return True if G.adj(v) has duplicates
    for v in G.vertices():
        # refactor to use set()
        adj = sorted(G.adj(v))
        for i in range(len(adj) - 1):
            if adj[i] == adj[i + 1]:
                return True
    return False


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


BipartiteColors = namedtuple('BipartiteColors', ['colors', 'examined_count'])


# See Algorithms, p 547
def bipartite_colors(G):
    """Return a list of the vertex colors in a graph, if it is bipartite.

    Parameters
    ----------
    G : :class:`Graph`
        The graph to analyze.

    Returns
    -------
    list or None
        A list of the vertex colors in the graph, if it is bipartite.
        Otherwise, None.
    """

    def dfs(G, v, marked, colors):
        """Perform depth-first search recursively from vertex `v`."""
        marked[v] = True

        for w in G.adj(v):
            if not marked[w]:
                colors[w] = not colors[v]
                if not dfs(G, w, marked, colors):
                    return False
            elif colors[w] == colors[v]:
                return False

        return True

    marked = G.V * [False]
    colors = G.V * [False]
    is_bipartite = False

    for s in G.vertices():
        if not marked[s]:
            is_bipartite = dfs(G, s, marked, colors)

            if not is_bipartite:
                break

    return BipartiteColors(
        colors=colors if is_bipartite else None, examined_count=sum(marked)
    )


# Exercise 4.1.32
def parallel_edges(G, s):
    """Count the parallel edges in the graph, starting from vertex `s`.

    Parameters
    ----------
    G : :class:`Graph`
        The graph to analyze.
    s : int
        The source vertex from which to start the search.

    Returns
    -------
    int
        The number of parallel edges in the graph.
    """
    count = 0
    marked = G.V * [False]

    # Run BFS from `s`.
    q = Queue()
    marked[s] = True
    q.enqueue(s)

    while not q.is_empty:
        v = q.dequeue()
        neighbs = G.V * [False]  # boolean array of (possible) neighbors
        for w in G.adj(v):
            # Same as using a hash table since we have integer vertices.
            if neighbs[w]:
                count += 1
            else:
                neighbs[w] = True

            if not marked[w]:
                marked[w] = True
                q.enqueue(w)

    return count // 2  # undirected edges counted 2x


# Exercise 4.1.36
class Biconnected:
    __doc__ = f"""Implements depth-first search to determine if a graph is
    edge-connected, aka biconnected.
    {_SEARCH_DOC}"""

    def __init__(self, G):
        self.Nbridges = 0
        self._count = 0  # depth counter
        self._pre = G.V * [None]  # order in which DFS examines v
        self._low = G.V * [None]  # lowest preorder of any vertex adjacent to v
        self._art = G.V * [False]  # is the vertex an articulation point?
        for s in G.vertices():
            if self._pre[s] is None:
                self._dfs(G, s, s)

    @property
    def is_edge_connected(self):
        """Return True if the graph is edge-connected."""
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
        if search.has_path_to(v):
            print(f"{v} ", end='')
    print()
    if search.count != G.V:
        print('NOT ', end='')
    print('connected.')
    return search


def print_paths(G, s, GS=DepthFirstSearch):
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
    bfs = BreadthFirstSearch(sg.G, s)
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
    DATA_PATH = Path(__file__).parents[3] / 'data'
    G = Graph.fromfile(DATA_PATH / 'tinyG.txt')
    G2 = Graph.fromfile(DATA_PATH / 'tinyG2.txt')

    print('----- DFS -----')
    print_dfs(G, 0)
    print_dfs(G, 9)

    # Test paths
    print('----- Connected Graph -----')
    GC = Graph.fromfile(DATA_PATH / 'tinyCG.txt')
    print(GC)
    print_dfs(GC, 0)

    print('----- DFS Paths -----')
    print_paths(GC, 0, GS=DepthFirstSearch)

    print('----- BFS Paths -----')
    print_paths(GC, 0, GS=BreadthFirstSearch)

    # Test connected components
    print('----- CC -----')
    comps = print_components(G2)
    comps20 = print_components(G2, vertices=comps[0])

    # Test connected components
    print('----- SymbolGraph -----')
    sg = SymbolGraph.fromfile(DATA_PATH / 'routes.txt')
    print('--- adjacency lists ---')
    print_adj(sg, 'JFK')
    print_adj(sg, 'LAX')
    print('--- shortest paths ---')
    degrees_of_separation(sg, 'JFK', 'LAS')
    degrees_of_separation(sg, 'JFK', 'DFW')

    sg = SymbolGraph.fromfile(DATA_PATH / 'movies.txt', delim='/')
    print('--- adjacency lists ---')
    print_adj(sg, 'Top Gun (1986)')
    print('--- shortest paths ---')
    degrees_of_separation(sg, 'Animal House (1978)', 'Titanic (1997)')
    degrees_of_separation(sg, 'Bacon, Kevin', 'Cruise, Tom')

    print('----- Graph Properties of mediumG -----')
    Gm = Graph.fromfile(DATA_PATH / 'mediumG.txt')
    # NOTE maximum recursion depth reached in largeG!
    # gc = Graph.fromfile(DATA_PATH / 'largeG.txt', verbose=True)

    gp = GraphProperties(Gm)
    print('        ϵ:', gp.eccentricity(0))
    print(' diameter:', gp.diameter())
    print('   radius:', gp.radius())
    print('   center:', gp.center())
    print('periphery:', gp.periphery())
    print('    girth:', gp.girth())
    assert gp.eccentricity(gp.center()[0]) == gp.radius()

    print('--- Cycle Paths ---')
    cp = find_cycle_path(Gm, 0, recursive=True)
    print('   path:', cp)
    cp_nr = find_cycle_path(Gm, 0, recursive=False)
    print('path nr:', cp_nr)
    assert cp == cp_nr
    cm = find_min_cycle(Gm, 0)
    print('minpath:', cm)

    print('complement', complement_graph(GC))
    bfs_cx = BreadthFirstSearch(complement_graph(GC), 0)
    bfs_c = ComplementBFS(GC, 0)
    print(bfs_cx.path_to(4))  # [0, 4]
    print(bfs_c.path_to(4))  # [0, 4]
    print(bfs_cx.path_to(2))  # [0, 4, 5, 2]
    print(bfs_c.path_to(2))  # [0, 4, 5, 2]

# =============================================================================
# =============================================================================
