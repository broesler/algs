#!/usr/bin/env python3
# =============================================================================
#     File: directed.py
#  Created: 2022-06-28 21:49
#   Author: Bernie Roesler
# =============================================================================

"""Implementations of undirected graph representations and associated algorithms.

See Sedgewick and Wayne, §4.2.
"""

from collections import namedtuple
from math import inf

from algs.basics import Queue, Stack
from algs.graph.base import BaseGraph
from algs.graph.search import BreadthFirstSearch, DepthFirstSearch
from algs.graph.undirected import CC, SymbolGraph


# -----------------------------------------------------------------------------
#         Graphs
# -----------------------------------------------------------------------------
class Digraph(BaseGraph):
    __doc__ = BaseGraph._DOC_TEMPLATE.format(
        descr="Implements a digraph using an array of adjacency lists."
    )

    def __init__(self, V=0, edges=None, parallel=True, self_loops=True):
        self._indegree = V * [0]
        super().__init__(V=V, edges=edges, parallel=parallel, self_loops=self_loops)

    def add_edge(self, v, w):
        """Add a directed edge from `v` to `w`."""
        self._validate_vertex(v)
        self._validate_vertex(w)
        # Exercise 4.2.5 no self-loops
        if not self._self_loops and v == w:
            raise ValueError(f"{v} == {w}! No self-loops allowed.")
        if self._parallel or not self.has_edge(v, w):
            self._E += 1
            self._adj[v].add(w)  # direction matters! Only change from Graph
            self._indegree[w] += 1

    def indegree(self, v):
        """Return the number of edges to `v`."""
        return self._indegree[v]

    def outdegree(self, v):
        """Return the number of edges from `v`."""
        return self.adj(v).size

    # Exercise 4.2.7
    @property
    def sources(self):
        """Return a list of vertices with indegree 0."""
        return [v for v in self.vertices() if self._indegree[v] == 0]

    # Exercise 4.2.7
    @property
    def sinks(self):
        """Return a list of vertices with outdegree 0."""
        return [v for v in self.vertices() if self.outdegree(v) == 0]

    # Exercise 4.2.7
    @property
    def is_map(self):
        """Return True if `G` is a map from the set of integers [0, V-1] onto
        itself.
        """
        return self._self_loops and all(self.outdegree(v) == 1 for v in self.vertices())

    def reverse(self):
        """Return the reverse of this digraph."""
        R = self.__class__(self._V)
        for v in self.vertices():
            for w in self.adj(v):
                R.add_edge(w, v)
        return R


class SymbolDigraph(SymbolGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, kind=Digraph)


# -----------------------------------------------------------------------------
#         Paths/Searches
# -----------------------------------------------------------------------------
# Algorithm 4.4: DirectedDFS == DepthFirstSearch!


def directed_cycle(G):
    """Find a directed cycle in a graph.

    Parameters
    ----------
    G : :class:`Digraph`
        The graph in which to search for a cycle.

    Returns
    -------
    cycle : list
        A list of vertices in the cycle, in order. Empty if no cycle exists.
    """
    marked = G.V * [False]
    edge_to = G.V * [None]
    on_stack = G.V * [False]

    def dfs(G, v):
        """Perform DFS recursively from vertex `v`."""
        on_stack[v] = True
        marked[v] = True

        for w in G.adj(v):
            if not marked[w]:
                edge_to[w] = v
                cycle = dfs(G, w)
                if cycle:
                    return cycle
            elif on_stack[w]:
                # Found a cycle, reconstruct it by backtracking up the stack
                cycle = Stack()
                x = v
                while x != w:
                    cycle.push(x)
                    x = edge_to[x]
                cycle.push(w)
                cycle.push(v)
                return cycle

        on_stack[v] = False
        return None

    # Run DFS from each vertex
    for v in G.vertices():
        if not marked[v]:
            cycle = dfs(G, v)
            if cycle:
                return list(cycle)

    return []  # no cycle found


DepthFirstOrder = namedtuple('DepthFirstOrder', ['pre', 'post', 'reverse_post'])


def depth_first_order(G):
    """Compute the pre-, post-, and reverse post-order traversals of the
    digraph.

    Parameters
    ----------
    G : :class:`Digraph`
        The graph for which to compute the orders.

    Returns
    -------
    DepthFirstOrder : :class:`namedtuple`
        A named tuple containing the pre-, post-, and reverse post-order
        traversals of the graph.
    """
    pre = Queue()
    post = Queue()
    reverse_post = Stack()
    marked = G.V * [False]

    def dfs(G, v):
        pre.enqueue(v)
        marked[v] = True
        for w in G.adj(v):
            if not marked[w]:
                dfs(G, w)
        post.enqueue(v)
        reverse_post.push(v)

    # Run DFS from each vertex
    for v in G.vertices():
        if not marked[v]:
            dfs(G, v)

    return DepthFirstOrder(list(pre), list(post), list(reverse_post))


# Algorithm 4.5
def topological_order(G):
    """Compute the topological ordering of a digraph.

    Parameters
    ----------
    G : :class:`Digraph`
        The graph for which to compute the topological order.

    Returns
    -------
    order : list or None
        A list of vertices in topological order. None if the graph is not a
        DAG.
    """
    # If the graph is a DAG, it has an order
    if directed_cycle(G):
        return None
    else:
        dfs = depth_first_order(G)
        return list(dfs.reverse_post)


# Algorithm 4.6
class KosarajuSCC(CC):
    """Kosaraju's algorithm for computing strong components."""

    def __init__(self, G):
        order = depth_first_order(G.reverse()).reverse_post
        super().__init__(G, vertices=order)

    def strongly_connected(self, v, w):
        """Return True if `v` and `w` are strongly connected."""
        return self.connected(v, w)  # semantic distinction


class TransitiveClosure:
    """The transitive closure of a digraph.

    .. note:: This algorithm uses O(V²) space and O(V(V+E)) time!
        Each DFS uses O(V) space, and takes O(V+E) time, and we repeat the
        search for each of the V vertices in G.
    """

    def __init__(self, G):
        self._all = G.V * [None]
        for v in G.vertices():
            self._all[v] = DepthFirstSearch(G, v)

    def reachable(self, v, w):
        """Return True if `w` is reachable from `v`."""
        return self._all[v].has_path_to(w)


# Exercise 4.2.20
def eulerian_cycle(G):
    """Find a cycle that visits each edge exactly once.

    Parameters
    ----------
    G : :class:`Digraph`
        The graph in which to search for the cycle.

    Returns
    -------
    cycle : list
        A list of vertices in the cycle, in order. Empty if no such cycle exists.
    """
    assert G.E > 0
    edge_to = G.V * [None]
    on_stack = G.V * [False]

    def non_isolated_vertex(G):
        """Return the first found vertex that is not a sink."""
        for v in G.vertices():
            if G.outdegree(v) > 0:
                return v
        raise ValueError('No vertices have outward edges!')

    def dfs(G, v):
        """Perform DFS recursively from vertex `v`."""
        on_stack[v] = True
        for w in G.adj(v):
            if outdegree[w] > 0:
                outdegree[v] -= 1
                indegree[w] -= 1
                edge_to[w] = v
                cycle = dfs(G, w)
                if cycle:
                    return cycle
            elif on_stack[w]:
                outdegree[v] -= 1
                indegree[w] -= 1
                # Found a cycle, backtrack up the stack
                cycle = Stack()
                x = v
                while x != w:
                    cycle.push(x)
                    x = edge_to[x]
                cycle.push(w)
                cycle.push(v)
                return cycle

        on_stack[v] = False
        return None

    # If degrees are not equal, Eulerian path cannot exist
    for v in G.vertices():
        if G.indegree(v) != G.outdegree(v):
            return []

    # Start with any vertex that is not a sink
    s = non_isolated_vertex(G)

    # Copy counts of edges into/out of vertices to "mark" edges
    indegree = G._indegree.copy()
    outdegree = [G.outdegree(v) for v in G.vertices()]

    # Find the cycle
    cycle = dfs(G, s)

    # Check if the cycle is valid
    is_valid = (
        cycle.size == G.E + 1
        and all(x == 0 for x in indegree)
        and all(x == 0 for x in outdegree)
    )

    return list(cycle) if is_valid else []


# Exercise 4.2.24, 4.2.25
def hamiltonian_path(G):
    """Find a path in a DAG that visits each vertex exactly once.

    This function computes a toplogical sort and then checks if there is an
    edge between each consecutive pair of vertices in the toplogical order.

    Parameters
    ----------
    G : :class:`Digraph`
        A DAG.

    Returns
    -------
    result : list
        The Hamiltonian path. Empty if it does not exist.
    """
    assert G.V > 0
    order = topological_order(G)

    if not order:
        raise ValueError("Input is not a DAG!")

    if len(order) == 1:
        return order

    # Check if each consecutive pair of vertices in the topological order has
    # an edge between them. If not, then there is no Hamiltonian path.
    for i in range(len(order) - 1):
        v = order[i]
        w = order[i + 1]
        if not G.has_edge(v, w):
            return []

    return order


# Exercise 4.2.9
def check_topological(G, order):
    """Return True if `order` is a topological order of `G`.

    Parameters
    ----------
    G : :class:`Digraph`
        The graph for which to check the order.
    order : iterable
        A list of vertices in some order.

    Returns
    -------
    result : bool
        True if `order` is a topological order of `G`, False otherwise.
    """
    if not topological_order(G):
        raise ValueError('G is not a DAG!')
    if sorted(order) != sorted(G.vertices()):
        raise ValueError("order is not a permutation of G's vertices!")
    # Check if each vertex in the given order has all of its adjacent vertices
    # *later* in the order.
    index = {v: i for i, v in enumerate(order)}
    for v in order:
        for w in G.adj(v):
            if index[w] < index[v]:
                return False
    return True


# Exercise 4.2.21: Lowest Common Ancestor
def vertex_height(G, source=None):
    """Compute the height of each vertex in a DAG.

    The *height* of a vertex is defined as the length of the longest path from
    the source to the vertex.

    Parameters
    ----------
    G : :class:`Digraph`
        A DAG.
    source : int or list of int, optional
        The source vertex or vertices from which to compute the heights. If
        None, the first vertex in the topological order of `G` is used as the
        source.

    Returns
    -------
    height : list
        A list of heights for each vertex in `G`.
    """
    order = topological_order(G)

    if order is None:
        raise ValueError("G is not a DAG!")

    if source is None:
        height = G.V * [0]
    else:
        height = G.V * [-inf]

        if isinstance(source, int):
            source = [source]

        for s in list(source):
            height[s] = 0

    for v in order:
        if height[v] == float(-inf):
            continue  # unreachable from s

        for w in G.adj(v):
            height[w] = max(height[w], height[v] + 1)

    return height


def get_ancestors(G, v):
    """Find the list of all ancestors of a vertex `v` in a graph."""
    # NOTE this method is Θ(2 V + E) because we go through the vertices again.
    # We could write a custom DFS that builds the list as it goes, but this way
    # is cleaner code.
    # Ancestors are all vertices that are reachable in the reverse graph
    dfs = DepthFirstSearch(G.reverse(), v)
    return [x for x in G.vertices() if dfs.has_path_to(x)]


class LowestCommonAncestor:
    """Find the lowest common ancestor of two vertices in a DAG.

    Parameters
    ----------
    G : :class:`Digraph`
        A DAG.
    s : int, optional
        The source vertex from which to compute the lowest common ancestor. If
        None, the first vertex in the topological order of `G` is used as the
        source.
    """

    def __init__(self, G, s=None):
        self._G = G
        self._s = s
        self._height = vertex_height(G, s)

    def __call__(self, v, w):
        """Return the lowest common ancestor of `v` and `w`.

        Parameters
        ----------
        v, w : int
            The vertices for which to find the lowest common ancestor.

        Returns
        -------
        int or None
            The lowest common ancestor of `v` and `w`, or None if no common
            ancestor exists.
        """
        if self._height[v] == -inf or self._height[w] == -inf:
            raise ValueError(f"One or both vertices {v}, {w} are not reachable!")

        ancestors_v = set(get_ancestors(self._G, v))
        ancestors_w = set(get_ancestors(self._G, w))
        common_ancestors = ancestors_v & ancestors_w

        if len(common_ancestors) == 0:
            return None

        return max(common_ancestors, key=lambda x: self._height[x])


# Exercise 4.2.22
ShortestAncestralPath = namedtuple(
    'ShortestAncestralPath', ['ancestor', 'path_from_v', 'path_from_w']
)


def shortest_ancestral_path(G, v, w):
    """Find the shortest ancestral path between two vertices in a DAG.

    Parameters
    ----------
    G : :class:`Digraph`
        A DAG.
    v, w : int
        The vertices for which to find the shortest ancestral path.

    Returns
    -------
    result : :class:`namedtuple` or None
        None if no common ancestor exists. Otherwise, a named tuple containing
        the following attributes:

        ancestor : int or None
            The common ancestor of `v` and `w` that is on the shortest
            ancestral path. None if no such ancestor exists.
        path_from_v, path_from_w : lists
            The paths from `v` or `w` to the common ancestor. None if no such
            path exists.
        length : int
            The length of the shortest ancestral path between `v` and `w`. -1
            if no such path exists.
    """
    if directed_cycle(G):
        raise ValueError("G is not a DAG!")

    G_R = G.reverse()
    targets = (v, w)

    bfs = {x: BreadthFirstSearch(G_R, x) for x in targets}
    ancestors = {u: {x for x in G.vertices() if bfs[u].has_path_to(x)} for u in targets}
    common_ancestors = ancestors[v] & ancestors[w]

    if len(common_ancestors) == 0:
        return None

    shortest_x = min(
        common_ancestors, key=lambda x: bfs[v].dist_to(x) + bfs[w].dist_to(x)
    )
    path_from = {u: list(bfs[u].path_to(shortest_x)) for u in targets}

    return ShortestAncestralPath(
        ancestor=shortest_x, path_from_v=path_from[v], path_from_w=path_from[w]
    )


# Exercise 4.2.23
def strong_component(G, v):
    """Return the strong component containing vertex `v` in a digraph.

    Parameters
    ----------
    G : :class:`Digraph`
        A digraph.
    v : int
        The vertex for which to find the strong component.

    Returns
    -------
    component : list
        A list of vertices in the strong component containing `v`.
    """
    dfs = DepthFirstSearch(G, v)
    forward_reachable = {x for x in G.vertices() if dfs.has_path_to(x)}
    dfs_r = DepthFirstSearch(G.reverse(), v)
    backward_reachable = {x for x in G.vertices() if dfs_r.has_path_to(x)}
    return list(forward_reachable & backward_reachable)


def quadratic_strong_components(G):
    """Find the strongly connected components of `G` in quadratic time.

    Parameters
    ----------
    G : :class:`Digraph`
        A digraph.

    Returns
    -------
    components : list of lists
        A list of strongly connected components, each of which is a list of
        vertices.
    """
    sccs = []
    marked = G.V * [False]

    for v in G.vertices():
        if not marked[v]:
            component = strong_component(G, v)  # O(V + E)
            for w in component:
                marked[w] = True
            sccs.append(component)

    return sccs

# =============================================================================
# =============================================================================
