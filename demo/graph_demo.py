#!/usr/bin/env python3
# =============================================================================
#     File: graph_demo.py
#  Created: 2026-06-12 13:39
#   Author: Bernie Roesler
# =============================================================================

"""Demo usage of graph implementations."""

from pathlib import Path

from graph_util import (
    degrees_of_separation,
    print_adj,
    print_components,
    print_dfs,
    print_paths,
)

from algs.graph.search import (
    BreadthFirstSearch,
    ComplementBFS,
    DepthFirstSearch,
    find_cycle_path,
    find_min_cycle,
)
from algs.graph.undirected import (
    Graph,
    GraphProperties,
    SymbolGraph,
    complement_graph,
)

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
