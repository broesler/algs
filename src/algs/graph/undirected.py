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

from collections import deque, namedtuple
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from tqdm import tqdm

from algs.basics import Bag, Queue, Stack
from algs.graph.base import BaseGraph
from algs.graph.search import (
    BreadthFirstSearch,
    GraphSearch,
    _reconstruct_path,
)
from algs.search import HashST, MultiHashSet
from algs.unionfind import WeightedQuickUnionUF


class Graph(BaseGraph):
    __doc__ = BaseGraph._DOC_TEMPLATE.format(
        descr="""An undirected graph represented as an array of adjacency lists.

        *See*: Sedgewick and Wayne, *Algorithms*, 4ed, p 526.
        """
    )

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

    def degree(self, v):
        """Return the degree of vertex `v`."""
        self._validate_vertex(v)
        return len(self._adj[v])

    @property
    def max_degree(self):
        """The maximum degree all vertices in the graph."""
        return max([self.degree(v) for v in self.vertices()])

    @property
    def avg_degree(self):
        """The average degree of the vertices in the graph."""
        return 2 * self._E / self._V

    # Exercise 4.1.32
    @property
    def num_parallel_edges(self):
        """The number of parallel edges in the graph."""
        return super().num_parallel_edges // 2  # each edge counted twice

    @property
    def num_self_loops(self):
        """The number of self-loops in the graph."""
        return super().num_self_loops // 2  # each edge counted twice


class SimpleGraph(Graph):
    __doc__ = BaseGraph._DOC_TEMPLATE.format(
        descr="""Implements a graph using an array of adjacency lists, with no
        self-loops or parallel edges allowed.
        """
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, self_loops=False, parallel=False)


class SymbolGraph:
    """A symbol graph.

    *See*: Sedgewick and Wayne, *Algorithms*, 4ed, p 552.

    Parameters
    ----------
    keys : iterable, optional
        An iterable of vertex labels (*e.g.* strings). If not given, vertices
        will be numbered from 0 to V-1.
    edges : iterable of pairs, optional
        An iterable of pairs of vertex labels denoting edges. If not given, the
        graph will be initialized with no edges.
    kind : type, optional
        The type of graph to use for the underlying graph structure.
    **kwargs : keyword arguments
        Additional keyword arguments to be passed to the underlying graph
        constructor.
    """

    def __init__(self, keys=None, edges=None, kind=Graph, **kwargs):
        self._st = HashST()  # map : str -> int
        self._keys = None  # map : int -> str
        self._GraphClass = kind
        self._G = None
        if keys is None:
            self._G = self._GraphClass(V=0, edges=None, **kwargs)
        else:
            # Build the symbol table
            for i, k in enumerate(keys):
                self._st[k] = i

            self._keys = keys

            # Underlying graph takes integer indices only
            int_edges = None
            if edges is not None:
                int_edges = ((self._st[v], self._st[w]) for v, w in edges)

            self._G = self._GraphClass(V=len(keys), edges=int_edges, **kwargs)

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
        sg._G = sg._GraphClass(V)
        with Path(filename).open() as fp:
            for line in fp.readlines():
                words = line.strip().split(delim)
                v = sg._st[words[0]]
                for w in words[1:]:
                    sg._G.add_edge(v, sg._st[w])

        return sg

    @property
    def graph(self):
        """The underlying graph structure."""
        return self._G

    @property
    def V(self):
        """The number of vertices in the graph."""
        return self._G.V

    def __contains__(self, k):
        """Return True if `k` is a vertex."""
        return k in self._st

    def index_of(self, k):
        """Return the index associated with `k`."""
        return self._st[k]

    def name_of(self, i):
        """Return the name associated with vertex index `i`."""
        return self._keys[i]

    # Implement Graph methods with names as arguments
    def vertices(self):
        """Return an iterable over the vertices."""
        return [self.name_of(v) for v in self._G.vertices()]

    def adj(self, v):
        """Return an iterable of vertices adjacent to `v`."""
        return [self.name_of(w) for w in self._G.adj(self.index_of(v))]

    def has_edge(self, v, w):
        """Return True if an edge from `v` to `w` exists."""
        return self._G.has_edge(self.index_of(v), self.index_of(w))

    def add_edge(self, v, w):
        """Add an edge from `v` to `w`."""
        return self._G.add_edge(self.index_of(v), self.index_of(w))


# Exercise 4.1.37
class EuclideanGraph(Graph):
    __doc__ = BaseGraph._DOC_TEMPLATE.format(
        descr="""An undirected graph whose vertices are points in the plane
        with coordinates.""",
    )

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
    __doc__ = BaseGraph._DOC_TEMPLATE.format(
        descr="""An undirected graph whose vertices are points in the plane
        with coordinates. Also include a symbol table of paths denoting the
        "routes" in the transportation system."""
    )

    def __init__(self, *args, routes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.routes = dict(routes)


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

    @property
    def count(self):
        """Return the number of connected components."""
        return self._count

    @property
    def is_connected(self):
        """True if every vertex is reachable from every other vertex."""
        return self._count == 1

    def get_components(self, sort=True):
        """Return a list of lists of vertices in each component."""
        components = [[] for _ in range(self._count)]

        for v in self._vs:
            components[self._id[v]].append(v)

        if sort:
            # Sort each component
            for c in components:
                c.sort()

            # Sort the overall list
            components.sort()

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


# Exercise 4.1.36
class Biconnected:
    """Depth-first search to determine if a graph is
    edge-connected, aka biconnected.

    Attributes
    ----------
    Nbridges : int
        The number of bridges in the graph. A bridge is an edge whose removal
        disconnects the graph. A graph is edge-connected if it has no bridges.
    is_edge_connected : bool
        True if the graph is edge-connected, False otherwise.
    """

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
        """True if the graph is edge-connected."""
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


# Web Exercise 31
def complement_graph(G):
    """Return a Graph that has an edge v-w iff v-w is not in `G`."""
    Gc = Graph(G.V)
    vs = set(range(G.V))
    for v in range(G.V):
        Gc._adj[v] = Bag(vs - set([v] + list(G.adj(v))))
    return Gc


# -----------------------------------------------------------------------------
#         Undirected Searches
# -----------------------------------------------------------------------------
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

    def __init__(self, G, source):
        if not isinstance(G, Graph):
            raise ValueError("UFSearch only works for undirected graphs!")

        super().__init__(G, source)  # populate self._sources

        self._uf = WeightedQuickUnionUF(G.V)
        for v in G.vertices():
            for w in G.adj(v):
                if not self._uf.connected(v, w):
                    self._uf.union(v, w)

        # Cache the roots for each source for O(1) access
        self._source_roots = {self._uf.find(s) for s in self._sources}

    @property
    def count(self):
        """The number of vertices connected to the sources.

        .. note::
           This value is not the same as the size of the component, since the
           sources may not be connected to all vertices in their respective
           components.
        """
        # Return the size of the component to which the source belongs
        # return self._uf._size[self._uf.find(self.s)]  # single source
        return sum(self._uf._size[root] for root in self._source_roots)

    def has_path_to(self, v):
        """Return True if `v` is connected to `s`."""
        return self._uf.find(v) in self._source_roots

    def path_to(self, v):
        """Not implemented since UF does not keep track of paths."""
        raise NotImplementedError("UFSearch does not keep track of paths!")


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


# =============================================================================
# =============================================================================
