#!/usr/bin/env python3
# =============================================================================
#     File: random.py
#  Created: 2022-06-21 17:54
#   Author: Bernie Roesler
#
"""
Functions to generate random graphs.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np

from algs.graph.undirected import Graph, EuclideanGraph, CC

π = np.pi
rng = np.random.default_rng(seed=19900416)


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
    if E < 1:
        raise ValueError(f"{E=} must be > 0")

    G = Graph(V)
    for v, w in rng.integers(V, size=(E, 2)):
        G.add_edge(v, w)

    assert G.V == V
    assert G.E == E
    return G


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
    if E < 1:
        raise ValueError(f"{E=} must be > 0")

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


def random_sparse_graph(V):
    """Generate a random, sparse graph with `V` vertices."""
    # Choose E between [V-1, ~cV**(3/2)] for sparsity
    E = rng.integers(V-1, V**1.4)
    return erdos_renyi(V, E)


def random_euclidean_graph(V, d=None, connected=None):
    """Generate a random, Euclidean graph by connecting `V` vertices to all
    points within radius `d` of each other."""
    if d is None and connected is None:
        raise ValueError('One of `d` or `connected` must be non-null.')
    if d is not None and not (0 <= d < 1):
        raise ValueError(f"{d=} must be in [0, 1)")
    if d is None:
        thresh = (np.log(V) / (π*V))**0.5
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
    D = np.sum(D**2, axis=-1)**0.5     # (V, V)
    # Connect vertices within threshold
    for v in range(V):
        for w in range(v+1, V):
            if D[v, w] < d:
                G.add_edge(v, w)
    return G


if __name__ == "__main__":
    V, E = 10, 9
    G = erdos_renyi(V, E)
    print(G)

    Gs = random_simple_graph(V, E)
    print(Gs)

    Ge = random_euclidean_graph(V, d=0.5)
    Gb = random_euclidean_graph(V, connected=True)
    fig, ax = plt.subplots(num=1, clear=True, constrained_layout=True)
    Ge.draw(ax=ax, label_nodes=True)
    Gb.draw(ax=ax, label_nodes=True, c='C0')
    plt.show()

    # c = CC(G)
    # print(c.get_components())


# =============================================================================
# =============================================================================
