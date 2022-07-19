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
from pathlib import Path

from algs.adt import Interval1D
from algs.unionfind import full_grid, random_grid
from algs.graph.undirected import (SimpleGraph, Graph, EuclideanGraph,
                                   SymbolGraph, TransportationGraph)

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
    maxE = V * (V-1) / 2
    if E < 1 or E > maxE:
        raise ValueError(f"{E=} must be in [1, {maxE}] for an undirected"
                         f"graph with {V=} vertices.")

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
    maxE = V * (V-1) / 2
    if E < 1 or E > maxE:
        raise ValueError(f"{E=} must be in [1, {maxE}] for an undirected"
                         f"graph with {V=} vertices.")

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
    edges = full_grid(V)     # generate all neighbor edges
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
    ints = sorted([Interval1D(lo, lo+d) for lo in rng.random(V)*(1-d)],
                  key=Interval1D.MIN_ORDER)
    edges = list()
    for i in range(V):
        for j in range(i+1, V):
            if ints[i].intersects(ints[j]):
                edges.append((i, j))
            else:
                break  # ordered, so if they don't intersect, we're done.
    return SymbolGraph(ints, edges)


# Exercise 4.1.46
def transport_graph(filename, key_file=None, loc_file=None):
    """Define a transportation graph based on an input file of paths.

    The transportation file format is as follows:
        line_name_0: 0-3-1-9-5-12-10-21-...
        line_name_1: 0-3-1-9-5-12-10-21-...
        ...

    If `key_file` or `loc_file` are given, create a symbol table of vertex
    names and/or the planar coordinates of the vertices.

    The `key_file` format is:
        ID KEY
        0 key0
        1 key1
        2 key2
        ...

    The `loc_file` format is:
        Location, X, Y
        key0, x, y
        key1, x, y
        ...
    """
    edges = list()
    routes = dict()  # named (ordered) list of vertices in the system
    with open(Path(filename), 'r') as fp:
        for line in fp.readlines():
            words = line.strip().split(':')
            path = [int(w) for w in words[1].split('-')]
            routes[words[0]] = path[1:]  # FIXME HACK skip 0
            for i in range(len(path)-1):
                edges.append((path[i], path[i+1]))
    V = 1 + max(max(edges))
    TG = TransportationGraph(SimpleGraph(V=V, edges=edges), routes=routes)
    out = TG

    if key_file is not None:
        keys = dict()
        ids = dict()
        with open(Path(key_file), 'r') as fp:
            for line in fp.readlines():
                words = line.strip().split()
                idn = int(words[0])
                name = words[1]
                keys[idn] = name
                ids[name] = idn
        # Build a symbol graph
        sg = SymbolGraph()
        sg._keys = keys
        sg._st = ids
        sg.G = TG

        if loc_file is not None:
            # Read in coordinates mapping
            with open(Path(loc_file), 'r') as fp:
                for line in fp.readlines()[1:]:
                    words = line.strip().split(',')
                    name = words[0]
                    lat, lon = float(words[1]), float(words[2])
                    sg.G.set_coordinates(sg.index(name), lon, lat)
        out = sg
    return out


# -----------------------------------------------------------------------------
#         Tests
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Define the parameters
    V, E = 10, 9

    # Random graphs
    G = erdos_renyi(V, E)
    print(G)

    Gs = random_simple_graph(V, E)
    print(Gs)

    sgi = random_interval_graph(V=5, d=0.1)

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

    # Plot the Boston T
    # TODO
    # * use geopandas(?) to get actual basemap
    # * run DFS/BFS to get routes between stations, noting line for each and
    #   where change-overs occur (ala MBTA website/app)
    tg = transport_graph('../data/bostonT_lines.txt',
                         key_file='../data/bostonT_stations.txt',
                         loc_file='../data/bostonT_locs.txt')

    fig, ax = plt.subplots(num=4, clear=True, constrained_layout=True)
    tg.G.draw(ax=ax,
              vkws=dict(s=10, alpha=0.4),
              ekws=dict(lw=1, alpha=0.2)
              )

    # Plot the routes
    def line_colors(name):
        colors = dict({'Blue': 'C0', 'Orange': 'C1', 'Green': 'C2',
                       'Red': 'C3', 'Silver': '#CCC', 'Mattapan': 'C3'})
        for k in colors.keys():
            if k in name:
                return colors[k]

    for name, route in tg.G.routes.items():
        tg.G.draw(p=route, ax=ax, c=line_colors(name),
                  # label_nodes=True, labels={i: tg.name(i) for i in route},
                  # vkws=dict(s=50, alpha=1.0, radius=1e-4, fontsize=8))
                  vkws=dict(s=20, alpha=1.0))

    # ax.axis('on')

    plt.show()

# =============================================================================
# =============================================================================
