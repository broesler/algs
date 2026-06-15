#!/usr/bin/env python3
# =============================================================================
#     File: random.py
#  Created: 2022-06-21 17:54
#   Author: Bernie Roesler
# =============================================================================

"""Functions to generate random graphs."""

import numpy as np

from algs.adt import Interval1D
from algs.graph.undirected import (
    EuclideanGraph,
    Graph,
    SymbolGraph,
)
from algs.unionfind import full_grid, random_grid

π = np.pi
rng = np.random.default_rng(seed=19900416)


# Exercise 4.1.39
def erdos_renyi(V, E):
    """Generate a random graph with `V` vertices and `E` edges.

    .. note:: This generator produces self-loops and parallel edges.

    Parameters
    ----------
    V : int
        The number of vertices.
    E : int
        The number of edges. The graph may only be connected if
        E ∈ [V-1, V(V-1)/2].

    Returns
    -------
    G : Graph
        An undirected graph with vertices labeled as integers [0, ..., V-1].
    """
    if V < 1:
        raise ValueError(f"{V=} must be > 0")
    maxE = V * (V - 1) / 2
    if E < 1 or E > maxE:
        raise ValueError(
            f"{E=} must be in [1, {maxE}] for an undirectedgraph with {V=} vertices."
        )

    G = Graph(V)
    for v, w in rng.integers(V, size=(E, 2)):
        G.add_edge(v, w)

    assert G.V == V
    assert G.E == E
    return G


# Exercise 4.1.40
def random_simple_graph(V, E):
    """Generate a random graph with `V` vertices and `E` edges.

    .. note:: This generator rejects self-loops and parallel edges.

    Parameters
    ----------
    V : int
        The number of vertices.
    E : int
        The number of edges. The graph may only be connected if
        E ∈ [V-1, V(V-1)/2].

    Returns
    -------
    G : Graph
        An undirected graph with vertices labeled as integers [0, ..., V-1].
    """
    if V < 1:
        raise ValueError(f"{V=} must be > 0")
    maxE = V * (V - 1) / 2
    if E < 1 or E > maxE:
        raise ValueError(
            f"{E=} must be in [1, {maxE}] for an undirectedgraph with {V=} vertices."
        )

    G = Graph(V)
    i = 0
    while i < E:
        v, w = rng.integers(V, size=2)  # could be slow for large E
        if v != w and not G.has_edge(v, w):
            G.add_edge(v, w)
            i += 1

    assert G.V == V
    assert G.E == E
    return G


# Exercise 4.1.41
def random_sparse_graph(V):
    """Generate a random, sparse graph with `V` vertices."""
    # Choose E between [V-1, ~cV**(3/2)] for sparsity
    E = rng.integers(V - 1, V**1.4)
    return erdos_renyi(V, E)


# Exercise 4.1.42
def random_euclidean_graph(V, d=None, connected=None):
    r"""Generate a random, Euclidean graph by connecting `V` vertices to all
    points within radius `d` of each other.

    Parameters
    ----------
    V : int
        The number of vertices.
    d : float in [0, 1], optional
        The radius within which vertices will be connected.
    connected : bool, optional
        If True, set `d` much greater than the threshold
        :math:`\sqrt{\frac{\log V}{\pi V}}`, such that the probability of
        a connected graph is ~ 1.
        Otherwise, set `d` to a fraction of the threshold, such that the
        probability of a connected graph is ~ 0.

    Returns
    -------
    G : EuclideanGraph
        An undirected graph with vertices labeled as integers [0, ..., V-1],
        each with (x, y) coordinates.
    """
    if d is None and connected is None:
        raise ValueError('One of `d` or `connected` must be non-null.')
    if d is not None and not (0 <= d <= 1):
        raise ValueError(f"{d=} must be in [0, 1]")
    if d is None:
        thresh = (np.log(V) / (π * V))**0.5
        if connected:
            d = 1.5 * thresh  # P ~ 1 that graph will be connected
        else:
            d = 0.5 * thresh  # P ~ 0 that graph will be connected
    # Generate random points in the unit square
    x, y = rng.random((2, V))
    G = EuclideanGraph(V=V, x=x, y=y)
    # Compute the pair-wise distance matrix
    p = np.c_[x, y]
    D = p[:, None, :] - p[None, :, :]  # (V, V, 2)
    D = np.sum(D**2, axis=-1)**0.5  # (V, V)
    # Connect vertices within threshold
    for v in range(V):
        for w in range(v + 1, V):
            if D[v, w] < d:
                G.add_edge(v, w)
    return G


def full_grid_graph(V, random=False):
    """Generate a graph where vertices are aligned on a `V`-by-`V` grid
    and connected to each of their neighbors.

    Parameters
    ----------
    V : int
        The number of vertices per side of the grid, such that the total number
        of vertices is `V^2`.
    random : bool
        If True, randomize the order of the edges.

    Returns
    -------
    G : EuclideanGraph
        An undirected graph with vertices labeled as integers [0, ..., V-1],
        with (x, y) coordinates.
    """
    Vsq = V**2  # total number of vertices
    edges = full_grid(V)  # generate all neighbor edges
    if random:
        rng.shuffle(edges)
    y, x = np.mgrid[:V, :V]  # vertex coordinates are on the grid
    x, y = np.ravel(x), np.ravel(y)
    return EuclideanGraph(V=Vsq, edges=edges, x=x, y=y)


# Exercise 4.1.43
def random_grid_graph(V, R=0, dist_edges=False):
    """Generate a random graph where vertices are aligned on a `V`-by-`V` grid
    and connected randomly to their neighbors.

    Parameters
    ----------
    V : int
        The number of vertices per side of the grid, such that the total number
        of vertices is `V^2`.
    R : int
        The number of extra random edges to add.
    dist_edges : bool
        If True, connect extra edge between vertices `s` and `t` with
        probability inversely proportional to the Euclidean distance between
        them.

    Returns
    -------
    G : EuclideanGraph
        An undirected graph with vertices labeled as integers [0, ..., V-1],
        with (x, y) coordinates.
    """
    E = V**2 - R
    Vsq = V**2  # number of vertices
    # Generate all neighbor edges, but in random order (as a RandomBag)
    edges = random_grid(V)
    edges = np.r_[[(p, q) for i, (p, q) in enumerate(edges) if i < E]]
    # Vertex coordinates are on the grid
    y, x = np.mgrid[:V, :V]
    x, y = np.ravel(x), np.ravel(y)
    # Generate R additional edges
    if R > 0:
        extra_edges = rng.integers(Vsq, size=(R, 2))
        if dist_edges:
            for v, w in extra_edges:
                r = ((x[v] - x[w])**2 + (y[v] - y[w])**2)**0.5  # [0, ∞)
                P = 1 / r if r else 0
                if rng.random() < P:
                    edges = np.r_[edges, [[v, w]]]
        else:
            edges = np.r_[edges, extra_edges]
    return EuclideanGraph(V=Vsq, edges=edges, x=x, y=y)


# Exercise 4.1.45
def random_interval_graph(V, d):
    """Define a graph consisting of `V` intervals of length `d` on the unit
    interval, connected if they intersect.

    Parameters
    ----------
    V : int
        The number of vertices.
    d : float in [0, 1]
        The length of the intervals.

    Returns
    -------
    G : Graph
        An undirected graph with vertices labeled as integers [0, ..., V-1].
    """
    if not (0 <= d <= 1):
        raise ValueError(f"{d=} must be in [0, 1]!")

    intervals = sorted(
        [Interval1D(lo, lo + d) for lo in rng.random(V) * (1 - d)],
        key=Interval1D.MIN_ORDER,
    )

    edges = []

    for i in range(V):
        for j in range(i + 1, V):
            if intervals[i].intersects(intervals[j]):
                edges.append((intervals[i], intervals[j]))
            else:
                break  # ordered, so if they don't intersect, we're done.

    return SymbolGraph(intervals, edges)


# =============================================================================
# =============================================================================
