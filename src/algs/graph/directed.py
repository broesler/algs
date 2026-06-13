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

from algs.basics import Queue, Stack
from algs.graph.base import BaseGraph
from algs.graph.search import DepthFirstSearch
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

    @property
    def sinks(self):
        """Return a list of vertices with outdegree 0."""
        return [v for v in self.vertices() if self.outdegree(v) == 0]

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
    order : list
        A list of vertices in topological order. Empty if the graph is not a
        DAG.
    """
    # If the graph is a DAG, it has an order
    if directed_cycle(G):
        return []
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
        return self._all[v].marked(w)


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
    outdegree = [G.outdegree(v) for v in G.vertices()]  # TODO?

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


# =============================================================================
# =============================================================================
