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

# import matplotlib.pyplot as plt
import numpy as np

from algs.graph.undirected import Graph, CC

rng = np.random.default_rng(seed=565656)


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

    g = Graph(V)
    vs, ws = rng.integers(V, size=(2, E))
    for i in range(E):
        g.add_edge(vs[i], ws[i])

    return g


if __name__ == "__main__":
    V, E = 10, 9
    G = erdos_renyi(V, E)
    print(G)

    c = CC(G)
    print(c.get_components())


# =============================================================================
# =============================================================================
