#!/usr/bin/env python3
# =============================================================================
#     File: graph_demo.py
#  Created: 2026-06-12 13:39
#   Author: Bernie Roesler
# =============================================================================

"""Demo usage of graph implementations."""

from pathlib import Path

from algs.graph.search import (
    BreadthFirstSearch,
    ComplementBFS,
    DepthFirstSearch,
    find_cycle_path,
    find_min_cycle,
)
from algs.graph.undirected import (
    CC,
    Graph,
    GraphProperties,
    SymbolGraph,
    complement_graph,
)


# -----------------------------------------------------------------------------
#         Client Functions
# -----------------------------------------------------------------------------
# Define some functions for use with graphs that would be too cumbersome to
# maintain in the basic API. See p 523.
# TODO move these into appropriate classes as methods
def max_degree(G, v):
    """Return the maximum degree all vertices in the graph."""
    return max([G.degree(v) for v in G.vertices()])


def avg_degree(G):
    """Compute the theoretical average degree of the graph."""
    return 2 * G.E / G.V


def self_loops(G):
    """Return the number of self-loops in the graph."""
    s = 0
    for v in G.vertices():
        for w in G.adj(v):
            if v == w:
                s += 1
    return s // 2  # each edge counted twice


def print_dfs(G, s, DFS=DepthFirstSearch):
    """Search the graph from vertex `s`."""
    # See p 529
    search = DFS(G, s)
    print(" ".join(str(v) for v in G.vertices() if search.has_path_to(v)))
    print(f"{'NOT ' if search.count != G.V else ''}connected.")
    return search


def print_paths(G, s, GS=DepthFirstSearch):
    """Search the graph from vertex `s`, returning the paths."""
    # See p 535
    search = GS(G, s)
    lines = []
    for v in G.vertices():
        prefix = f"{s:2d}->{v:2d}: "
        if search.has_path_to(v):
            path_str = "-".join(str(x) for x in search.path_to(v))
            lines.append(f"{prefix}{path_str}")
        else:
            lines.append(f"{prefix}not connected")
    print("\n".join(lines))


def print_components(G, vertices=None):
    """Compute the connected components in the graph.

    Parameters
    ----------
    G : :obj:`Graph`
        The graph to analyze.
    vertices : iterable, optional
        An iterable of the vertices to consider. If not given, all vertices
        in `G` will be used.

    Returns
    -------
    components : list of lists
        List of lists of the vertices in each connected component.
    """
    # See p 543
    vertices = vertices or G.vertices()
    cc = CC(G, vertices)
    M = cc.count()
    print(f"{M} components")
    components = cc.get_components()
    lines = [f"{i}: {' '.join(str(v) for v in c)}" for i, c in enumerate(components)]
    print("\n".join(lines))
    return components


def print_adj(sg, s):
    """Print the adjacency list of the source."""
    # See p 550
    print(f"{s}: {' '.join(w for w in sg.adj(s))}")


def degrees_of_separation(sg, source, sink):
    """Return the shortest path from source to sink in a symbol graph."""
    # See p 555
    if source not in sg:
        raise ValueError(f"{repr(source)} not in graph!")
    s = sg.index(source)
    bfs = BreadthFirstSearch(sg.G, s)
    if sink in sg:
        print(f"{source}->{sink}")
        t = sg.index(sink)
        if bfs.has_path_to(t):
            print('\n'.join(sg.name(v) for v in bfs.path_to(t)))
        else:
            print('Not connected.')
    else:
        raise ValueError(f"{repr(sink)} not in graph!")


# -----------------------------------------------------------------------------
#         Run Demo
# -----------------------------------------------------------------------------
DATA_PATH = Path(__file__).parents[1] / 'data'
G = Graph.fromfile(DATA_PATH / 'tinyG.txt')
G2 = Graph.fromfile(DATA_PATH / 'tinyG2.txt')

print('----- DFS -----')
print_dfs(G, 0)
print_dfs(G, 9)

# Test paths
print('----- Connected Graph -----')
GC = Graph.fromfile(DATA_PATH / 'tinyCG.txt')
print(GC)
print_dfs(GC, 0)

print('----- DFS Paths -----')
print_paths(GC, 0, GS=DepthFirstSearch)

print('----- BFS Paths -----')
print_paths(GC, 0, GS=BreadthFirstSearch)

# Test connected components
print('----- CC -----')
comps = print_components(G2)
comps20 = print_components(G2, vertices=comps[0])

# Test connected components
print('----- SymbolGraph -----')
sg = SymbolGraph.fromfile(DATA_PATH / 'routes.txt')
print('--- adjacency lists ---')
print_adj(sg, 'JFK')
print_adj(sg, 'LAX')
print('--- shortest paths ---')
degrees_of_separation(sg, 'JFK', 'LAS')
degrees_of_separation(sg, 'JFK', 'DFW')

sg = SymbolGraph.fromfile(DATA_PATH / 'movies.txt', delim='/')
print('--- adjacency lists ---')
print_adj(sg, 'Top Gun (1986)')
print('--- shortest paths ---')
degrees_of_separation(sg, 'Animal House (1978)', 'Titanic (1997)')
degrees_of_separation(sg, 'Bacon, Kevin', 'Cruise, Tom')

print('----- Graph Properties of mediumG -----')
Gm = Graph.fromfile(DATA_PATH / 'mediumG.txt')
# NOTE maximum recursion depth reached in largeG!
# gc = Graph.fromfile(DATA_PATH / 'largeG.txt', verbose=True)

gp = GraphProperties(Gm)
print('        ϵ:', gp.eccentricity(0))
print(' diameter:', gp.diameter())
print('   radius:', gp.radius())
print('   center:', gp.center())
print('periphery:', gp.periphery())
print('    girth:', gp.girth())
assert gp.eccentricity(gp.center()[0]) == gp.radius()

print('--- Cycle Paths ---')
cp = find_cycle_path(Gm, 0, recursive=True)
print('   path:', cp)
cp_nr = find_cycle_path(Gm, 0, recursive=False)
print('path nr:', cp_nr)
assert cp == cp_nr
cm = find_min_cycle(Gm, 0)
print('minpath:', cm)

print('complement', complement_graph(GC))
bfs_cx = BreadthFirstSearch(complement_graph(GC), 0)
bfs_c = ComplementBFS(GC, 0)
print(bfs_cx.path_to(4))  # [0, 4]
print(bfs_c.path_to(4))  # [0, 4]
print(bfs_cx.path_to(2))  # [0, 4, 5, 2]
print(bfs_c.path_to(2))  # [0, 4, 5, 2]

# =============================================================================
# =============================================================================
