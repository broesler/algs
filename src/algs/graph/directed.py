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
from pathlib import Path

from algs.basics import Queue, Stack
from algs.graph.undirected import CC, Graph, SymbolGraph, UndirectedGraph


# -----------------------------------------------------------------------------
#         Abstract Base Classes
# -----------------------------------------------------------------------------
class DirectedGraph(UndirectedGraph):
    # Extends the UndirectedGraph ABC.
    def reverse(self):
        """Return the reverse of this digraph."""
        R = self.__class__(self.V)
        for v in self.vertices():
            for w in self.adj(v):
                R.add_edge(w, v)
        return R


# -----------------------------------------------------------------------------
#         Graphs
# -----------------------------------------------------------------------------
class Digraph(DirectedGraph, Graph):
    __doc__ = f"""Implements a digraph using an array of adjacency lists.
    {UndirectedGraph.__doc__}"""

    def __init__(self, V, *args, **kwargs):
        self._indegree = V * [0]
        super().__init__(V, *args, **kwargs)

    def add_edge(self, v, w):
        """Add a directed edge from `v` to `w`."""
        self._validate_vertex(v)
        self._validate_vertex(w)
        # Exercise 4.2.5 no self-loops
        if not self._SELF_LOOPS and v == w:
            raise ValueError(f"{v} == {w}! No self-loops allowed.")
        if self._PARALLEL or not self.has_edge(v, w):
            self.E += 1
            self._adj[v].add(w)  # direction matters! Only change from Graph
            self._indegree[w] += 1

    def indegree(self, v):
        """Return the number of edges to `v`."""
        return self._indegree[v]

    def outdegree(self, v):
        """Return the number of edges from `v`."""
        return self.adj(v).size


class SymbolDigraph(SymbolGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, kind=Digraph)


# -----------------------------------------------------------------------------
#         Paths/Searches
# -----------------------------------------------------------------------------
# Algorithm 4.4
class DirectedDFS:
    """Implements depth-first search in a digraph."""

    def __init__(self, G, sources):
        """
        Parameters
        ----------
        G : :obj:`Digraph`
            The graph over which to search.
        sources : int or iterable
            A single source index, or an iterable of indices from which to
            begin the search.
        """
        self._marked = G.V * [False]
        try:
            for s in sources:
                self._dfs(G, s)
        except TypeError:
            self._dfs(G, sources)

    def marked(self, v):
        """Return True if a vertex has been visited."""
        return self._marked[v]

    def _dfs(self, G, v):
        self._marked[v] = True
        for w in G.adj(v):
            if not self._marked[w]:
                self._dfs(G, w)


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
    """Implements Kosaraju's algorithm for computing strong components."""

    def __init__(self, G):
        order = depth_first_order(G.reverse()).reverse_post
        super().__init__(G, vertices=order)

    def strongly_connected(self, v, w):
        """Return True if `v` and `w` are strongly connected."""
        return self.connected(v, w)  # semantic distinction


class TransitiveClosure:
    """Computes the transitive closure of a digraph.

    .. note:: This algorithm uses O(V²) space and O(V(V+E)) time!
        Each DFS uses O(V) space, and takes O(V+E) time, and we repeat the
        search for each of the V vertices in G.
    """

    def __init__(self, G):
        self._all = G.V * [None]
        for v in G.vertices():
            self._all[v] = DirectedDFS(G, v)

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
    d = Degrees(G)

    for v in G.vertices():
        if d.indegree(v) != d.outdegree(v):
            return []

    # Start with any vertex that is not a sink
    s = non_isolated_vertex(G)

    # Copy counts of edges into/out of vertices to "mark" edges
    indegree = d._indegree.copy()
    outdegree = d._outdegree.copy()

    # Find the cycle
    cycle = dfs(G, s)

    # Check if the cycle is valid
    is_valid = (
        cycle.size == G.E + 1
        and all(x == 0 for x in indegree)
        and all(x == 0 for x in outdegree)
    )

    if is_valid:
        return list(cycle)
    else:
        return []


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
        w = order[i+1]
        if not G.has_edge(v, w):
            return []

    return order



# -----------------------------------------------------------------------------
#         Graph Properties
# -----------------------------------------------------------------------------
# Exercise 4.2.7
class Degrees:
    """Compute the in- and outdegrees of each vertex."""

    def __init__(self, G):
        self._indegree = G.V * [0]
        self._outdegree = G.V * [0]
        for v in G.vertices():
            adj = G.adj(v)
            self._outdegree[v] = len(adj)
            for w in adj:
                self._indegree[w] += 1
        self._sources = [v for v in G.vertices() if self._indegree[v] == 0]
        self._sinks = [v for v in G.vertices() if self._outdegree[v] == 0]

    def indegree(self, v):
        """Return the number of edges pointing to `v`."""
        return self._indegree[v]

    def outdegree(self, v):
        """Return the number of edges pointing from `v`."""
        return self._outdegree[v]

    def sources(self):
        """Return a list of vertices with indegree 0."""
        return self._sources

    def sinks(self):
        """Return a list of vertices with outdegree 0."""
        return self._sinks

    @property
    def is_map(self):
        """Return True if `G` is a map from the set of integers [0, V-1] onto
        itself.
        """
        return G._SELF_LOOPS and all(x == 1 for x in self._outdegree)


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


# TODO move to tests/test_digraph.py
# -----------------------------------------------------------------------------
#         Tests
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    from random import shuffle

    from algs.graph.undirected import BreadthFirstPaths, DepthFirstPaths, print_paths

    DATA_PATH = Path(__file__).parents[3] / 'data'

    print('----- Digraph -----')
    G = Digraph.fromfile(DATA_PATH / 'tinyDG.txt')
    print(G)
    print('----- Reverse -----')
    R = G.reverse()
    print(R)

    print('----- DirectedDFS -----')
    dfs = DirectedDFS(G, 2)
    print(' '.join(f"{v} " for v in G.vertices() if dfs.marked(v)))
    dfs = DirectedDFS(G, [1, 2, 6])
    print(' '.join(f"{v} " for v in G.vertices() if dfs.marked(v)))

    print('----- DFS Paths -----')
    print_paths(G, 0, GS=DepthFirstPaths)
    print('----- BFS Paths -----')
    print_paths(G, 0, GS=BreadthFirstPaths)

    print('----- Cycle -----')
    cyc = directed_cycle(G)
    assert cyc
    print(cyc)

    print('----- Orders -----')
    p = depth_first_order(G)
    print(p.pre)
    print(p.post)
    print(p.reverse_post)
    assert list(reversed(p.post)) == p.reverse_post

    t = topological_order(G)
    assert not t

    sg = SymbolDigraph.fromfile(DATA_PATH / 'jobs.txt', delim='/')
    t = topological_order(sg.G)
    assert t
    print('\n'.join(sg.name(v) for v in t))

    cc = KosarajuSCC(G)
    assert cc.count() == 5
    print(cc.get_components())

    # Web Exercise 17
    Gm = Digraph.fromfile(DATA_PATH / 'mediumDG.txt')
    cc = KosarajuSCC(Gm)
    assert cc.count() == 10

    d = Degrees(G)
    assert d._indegree == [2, 1, 2, 2, 3, 2, 1, 1, 1, 3, 1, 1, 2]
    assert d._outdegree == [2, 0, 2, 2, 2, 1, 3, 2, 2, 2, 1, 2, 1]
    assert d.sources() == []
    assert d.sinks() == [1]

    G2 = Digraph.fromfile(DATA_PATH / 'tinyDG2.txt')
    print(G2)
    d = Degrees(G2)
    assert d._indegree == [1, 2, 2, 2, 1, 0, 2, 0, 2, 0, 2, 2]
    assert d._outdegree == [1, 1, 2, 2, 1, 2, 1, 2, 2, 0, 1, 1]
    assert d.sources() == [5, 7, 9]
    assert d.sinks() == [9]

    # Exercise 4.2.20: Eulerican cycle: Create a circular graph
    edges = []
    N = 5
    Gcyc = Digraph(N)
    for i in range(N):
        Gcyc.add_edge(i, (i + 1) % N)
    e = eulerian_cycle(Gcyc)
    print(e)

    Gno_cyc = Digraph(N)
    for i in range(N - 1):
        Gno_cyc.add_edge(i, i + 1)
    e = eulerian_cycle(Gno_cyc)
    assert not e

    print('----- DAGs -----')
    D = Digraph.fromfile(DATA_PATH / 'tinyDAG.txt')
    print(D)
    orders = depth_first_order(D)
    print('   pre:', orders.pre)
    print('  post:', orders.post)
    print('r_post:', orders.reverse_post)
    t = topological_order(D)
    print('  topo:', t)
    assert t == orders.reverse_post

    assert check_topological(D, t)
    shuffle(t)
    assert not check_topological(D, t)

    cc = KosarajuSCC(D)
    print(cc.get_components())

    # Exercise 4.2.24: Hamiltonian path
    h = hamiltonian_path(Gno_cyc)
    assert h == list(range(N))

    H = Digraph(N)
    j = N // 2
    for i in range(N - 1):
        if i == j:
            continue
        H.add_edge(i, i + 1)
    H.add_edge(j + 1, j)
    h = hamiltonian_path(H)
    assert not h

# =============================================================================
# =============================================================================
