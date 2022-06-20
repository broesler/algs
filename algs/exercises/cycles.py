#!/usr/bin/env python3
# =============================================================================
#     File: cycles.py
#  Created: 2022-06-19 22:09
#   Author: Bernie Roesler
#
"""
Exercise 4.1.30. Detecting Eulerian and/or Hamiltonian cycles.

Eulerian: Cycle that touches all edges.
Hamiltonian: Cycle that touches all vertices.
"""
# =============================================================================

from algs.graph import Graph, CyclePath


# TODO maodify CyclePath to include this check?
def has_eulerian(G):
    """Return True if a graph has an Eulerian cycle."""
    for s in G.vertices():
        c = CyclePath(G, s)
        p = c.cycle_path()
        if c.has_cycle and set(p) == set(G.vertices()):
            return True
    else:
        return False


def has_hamiltonian(G):
    """Return True if a graph has an Hamiltonian cycle."""
    for s in G.vertices():
        c = CyclePath(G, s)
        e = path_to_edges(c.cycle_path())
        if c.has_cycle and set(e) == set(G.edges()):
            return True
    else:
        return False


def path_to_edges(p):
    """Convert a list of vertices on a path to a list of tuples of edges."""
    return [(p[i], p[i+1]) for i in range(len(p)-1)]


# Define 4 graphs
G0 = Graph(10, [(0, 1), (0, 2), (0, 3), (1, 3), (1, 4), (2, 5), (2, 9), (3, 6),
                (4, 7), (4, 8), (5, 8), (5, 9), (6, 7), (6, 9), (7, 8)])

G1 = Graph(10, [(0, 1), (0, 2), (0, 3), (1, 3), (0, 3), (2, 5), (5, 6), (3, 6),
                (4, 7), (4, 8), (5, 8), (5, 9), (6, 7), (6, 9), (8, 8)])

G2 = Graph(10, [(0, 1), (1, 2), (1, 3), (0, 3), (0, 4), (2, 5), (2, 9), (3, 6),
                (4, 7), (4, 8), (5, 8), (5, 9), (6, 7), (6, 9), (7, 8)])

G3 = Graph(10, [(4, 1), (7, 9), (6, 2), (7, 3), (5, 0), (0, 2), (0, 8), (1, 6),
                (3, 9), (6, 3), (2, 8), (1, 5), (9, 8), (4, 5), (4, 7)])

for i, G in enumerate([G0, G1, G2, G3]):
    c = CyclePath(G, 0)
    if c.has_cycle:
        print(c.cycle_path())
        print(has_eulerian(G))
        print(has_hamiltonian(G))

# =============================================================================
# =============================================================================
