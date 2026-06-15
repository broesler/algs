#!/usr/bin/env python3
# =============================================================================
#     File: transport_graph.py
#  Created: 2026-06-15 13:59
#   Author: Bernie Roesler
# =============================================================================

"""Exercise 4.1.46: Transport Graph."""

from pathlib import Path

import matplotlib.pyplot as plt

from algs.graph.undirected import (
    SimpleGraph,
    SymbolGraph,
    TransportationGraph,
)

DATA_PATH = Path(__file__).parents[1] / 'data'


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
    edges = []
    routes = {}  # named (ordered) list of vertices in the system

    with Path(filename).open() as fp:
        for line in fp:
            if not line.strip():
                continue

            name, path_str = line.split(':')
            path = [int(w) for w in path_str.strip().split('-')]
            routes[name.strip()] = path[1:]  # FIXME HACK skip 0

            for i in range(len(path) - 1):
                edges.append((path[i], path[i + 1]))

    V = 1 + max(max(v, w) for v, w in edges)
    base_graph = SimpleGraph(V=V, edges=edges)
    TG = TransportationGraph(base_graph, routes=routes)

    if key_file is None:
        return TG

    keys = V * [""]
    ids = {}

    with Path(key_file).open() as fp:
        for line in fp:
            words = line.strip().split()
            if not words:
                continue

            idn = int(words[0])
            name = words[1]

            keys[idn] = name
            ids[name] = idn

    # Build a symbol graph
    sg = SymbolGraph()
    sg._keys = keys
    sg._st = ids
    sg._G = TG

    if loc_file is not None:
        # Read in coordinates mapping
        with Path(loc_file).open() as fp:
            next(fp)  # skip header
            for line in fp:
                words = line.strip().split(',')
                if not words:
                    continue

                name = words[0]
                lat, lon = float(words[1]), float(words[2])

                sg.graph.set_coordinates(sg.index_of(name), lon, lat)

    return sg


# ---------- Plot the Boston T ----------
# TODO
# * use geopandas(?) to get actual basemap
# * run DFS/BFS to get routes between stations, noting line for each and
#   where change-overs occur (ala MBTA website/app)
tg = transport_graph(
    DATA_PATH / 'bostonT_lines.txt',
    key_file=DATA_PATH / 'bostonT_stations.txt',
    loc_file=DATA_PATH / 'bostonT_locs.txt',
)

fig, ax = plt.subplots(num=1, clear=True)

tg.graph.draw(ax=ax, vkws={'s': 10, 'alpha': 0.4}, ekws={'lw': 1, 'alpha': 0.2})


def line_colors(name):
    """Return a color for a given line name.

    Allows lines like "GreenB" -> "Green".
    """
    colors = {
        'Blue': 'tab:blue',
        'Orange': 'tab:orange',
        'Green': 'tab:green',
        'Red': 'tab:red',
        'Silver': '#CCC',
        'Mattapan': 'tab:red',
    }
    for k, v in colors.items():
        if k in name:
            return v


# Plot the routes
for name, route in tg.graph.routes.items():
    tg.graph.draw(
        p=route,
        ax=ax,
        c=line_colors(name),
        # label_nodes=True, labels={i: tg.name(i) for i in route},
        # 'vkws':{'s':50, 'alpha':1.0, 'radius':1e-4, 'fontsize':8},
        vkws={'s': 20, 'alpha': 1.0},
    )

plt.show()

# =============================================================================
# =============================================================================
