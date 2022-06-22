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
import pandas as pd

from algs.adt import Interval1D
from algs.unionfind import random_grid
from algs.graph.undirected import Graph, EuclideanGraph, SymbolGraph

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
    if E < 1:
        raise ValueError(f"{E=} must be > 0")

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


# Exercise 4.1.41
def random_sparse_graph(V):
    """Generate a random, sparse graph with `V` vertices."""
    # Choose E between [V-1, ~cV**(3/2)] for sparsity
    E = rng.integers(V-1, V**1.4)
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


# Exercise 4.1.44
def random_DQgraph(V, E):
    """Create a random graph from Dairy Queen locations in the U.S."""
    df = pd.read_csv('../data/dairyqueen.csv', header=None)
    df.columns = ['lat', 'lon', 'name', 'address']
    rows = rng.integers(df.shape[0], size=V)
    df = df.iloc[rows]
    # Build a symbol graph using the names of the restaurants
    sg = SymbolGraph(keys=df['name'])
    sg.G = EuclideanGraph(random_simple_graph(V, E), x=df['lat'], y=df['lon'])
    return sg


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
    ints = [Interval1D(lo, lo+d) for lo in rng.random(V)]
    edges = list()
    # TODO use a BST instead of brute-forcing it
    for i in range(V):
        for j in range(i+1, V):
            if ints[i].intersects(ints[j]):
                edges.append((i, j))
    return SymbolGraph(ints, edges)


# Exercise 4.1.46
def random_transport_graph(filename, delim='-'):
    """Define a transportation graph based on an input file."""
    edges = list()
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            words = line.strip().split(delim)
            for i in range(len(words)-1):
                edges.append((words[i], words[i+1]))
    V = 1 + max(max(edges))
    return Graph(V=V, edges=edges)


# TODO get GPS coordinates for the stations, and compute distances
def _parse_bostonmetro():
    """Parse the 'bostonmetro.txt' file."""
    station_names = dict()  # map: id -> name
    station_ids = dict()    # map: name -> id
    tlines = dict()
    with open('../data/bostonmetro.txt', 'r') as fp:
        for line in fp.readlines()[1:]:
            words = line.strip().split()
            station_id = int(words[0])
            station_name = words[1]
            station_names[station_id] = station_name
            station_ids[station_name] = station_id
            ws = iter(words[2:])
            # Iterate over possibly multiple in/outbound lines
            # NOTE the return structure gives directional edges. We can use
            # these edges directly to build a (symbol) graph, but the tricky
            # part is (automatically) converting the list of tuples into
            # a path string like 0-1-2-6-5-12-4, etc.
            try:
                while True:
                    line_name = next(ws)
                    outbound = int(next(ws))
                    inbound = int(next(ws))
                    if line_name not in tlines:
                        tlines[line_name] = list()
                    # tlines[line_name].append((inbound, station_id))
                    # tlines[line_name].append((station_id, outbound))
                    tlines[line_name].append((inbound, station_id, outbound))
            except StopIteration:
                continue

    return station_names, station_ids, tlines


# FIXME this function is wrong. It outputs, e.g.:
#   GreenC: 0-34-41-47-51-54-56-58-61-63-68-73-74-76-77-80-81-83
# but for GreenC, the order should be 0-34-41-*51*-47-54-56-...
def _list_to_path(a):
    """Convert a sorted list of tuples [(0, 1), (1, 2), (2, 3), ...] to
    a string like '0-1-2-3-...'."""
    af = [leaf for tree in a for leaf in tree]
    af = sorted(set(af))  # sort integer values
    return '-'.join([str(x) for x in af])

    # NOTE this code on the right track... but fails for some cases
    # a = sorted(set(a))  # unique list of edges
    # s = ''
    # for i in range(len(a)-1):
    #     # Four cases:
    #     # 1. (a, b), (b, c) -> a-b-c
    #     if a[i][1] == a[i+1][0]:
    #         s += f"{a[i][0]}-{a[i][1]}-{a[i+1][1]}-"
    #     # 2. (b, a), (c, b) -> a-b-c
    #     elif a[i][0] == a[i+1][1]:
    #         s += f"{a[i][1]}-{a[i][0]}-{a[i+1][0]}-"
    #     # 3. (b, a), (b, c) -> a-b-c
    #     elif a[i][0] == a[i+1][0]:
    #         s += f"{a[i][0]}-{a[i][1]}-{a[i+1][1]}-"
    #     # 4. (a, b), (c, b) -> a-b-c
    #     elif a[i][1] == a[i+1][1]:
    #         s += f"{a[i][0]}-{a[i][1]}-{a[i+1][0]}-"
    #     else:
    #         raise ValueError(f"Stations do not connect! {(a[i], a[i+1])}")
    # return s


def _write_bostont_files(station_names, station_ids, tlines):
    # Write re-formatted output files
    with open('../data/bostont_stations.txt', 'w') as fp:
        for k, v in station_names.items():
            fp.write(f"{k} {v}\n")

    with open('../data/bostont_lines.txt', 'w') as fp:
        for k, v in tlines.items():
            fp.write(f"{k}: {_list_to_path(v)}\n")


# Intermediate structure:
# Line  , edges
# Orange, 2-1, 1-0, 5-2, 2-1, ...
# Blue, 4-3, 3-0, 6-4, 4-3, ...

# Q: how to sort the edges and combine into paths?

# Output file(s):
# 'bostont_lines.txt'
# Orange: 0-1-2-5-...
# Blue: 0-3-4-6-...
#
# 'bostont_stations.txt'
# 1 OakGrove
# 2 Malden
# ...

if __name__ == "__main__":
    # Define the parameters
    V, E = 10, 9

    # Random graphs
    G = erdos_renyi(V, E)
    print(G)

    Gs = random_simple_graph(V, E)
    print(Gs)

    sgi = random_interval_graph(V, d=0.1)

    # Plots
    Ge = random_euclidean_graph(V, d=0.5)
    Gb = random_euclidean_graph(V, connected=True)
    fig, ax = plt.subplots(num=1, clear=True, constrained_layout=True)
    Ge.draw(ax=ax, label_nodes=True)
    Gb.draw(ax=ax, label_nodes=True, c='C0')
    plt.show()

    Gg = random_grid_graph(V, R=20, dist_edges=True)
    fig, ax = plt.subplots(num=2, clear=True, constrained_layout=True)
    Gg.draw(ax=ax)

    sg = random_DQgraph(V=500, E=500)
    fig, ax = plt.subplots(num=3, clear=True, constrained_layout=True)
    sg.G.draw(ax=ax,
              vkws=dict(s=10, alpha=0.4),
              ekws=dict(lw=1, alpha=0.2)
              )

    station_names, station_ids, tlines = _parse_bostonmetro()

    plt.show()

# =============================================================================
# =============================================================================
