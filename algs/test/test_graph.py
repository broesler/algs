#!/usr/bin/env python3
#==============================================================================
#     File: test_graph.py
#  Created: 2019-03-03 23:31
#   Author: Bernie Roesler
#
"""
  Description: Test graph data structures
"""
#==============================================================================

import re
from algs import Digraph, DepthFirstSearch, DirectedCycle, BreadthFirstSearch
# from ..graph import Digraph, BreadthFirstSearch

# TODO import pytest

pat = re.compile('(\d+)\s+(\d+)')
def parse(line):
    match = pat.search(line)
    return int(match.group(1)), int(match.group(2))

# Load test file
# TODO loop over all test files
filename = 'test_data/tinyDG.txt'
# filename = 'test_data/tinyDAG.txt'
# filename = 'test_data/mediumDG.txt'

G = Digraph()
with open(filename, 'r') as file:
    for i, line in enumerate(file.readlines()):
        if i == 0: V = int(line.rstrip())
        if i == 1: E = int(line.rstrip())
        if i < 2: continue
        a, b = parse(line)
        G.add_edge(a, b)

# Test graph construction
# def test_graph_size():
assert G.V == V
assert G.E == E

# def test_source():
sources = G.roots()
# assert s == 7  # only for tinyDG.txt

# def test_reverse():
Gr = G.reverse()
for s in sources:
    assert Gr[s] == list([])  # source has no adjacents in reverse

# Test DFS
dfs = DepthFirstSearch(G, [sources[0]])

finder = DirectedCycle(G)
assert finder.has_cycle

# Test BFS
# bfs = BreadthFirstSearch(G, [s])
# print('Unordered BFS:')
# print('--------------')
# bfs.print_paths()

# Test Ordered BFS
# bfs_o = BreadthFirstSearch(G, [s], ordered=True)
# print('Ordered BFS:')
# print('------------')
# bfs_o.print_paths()

#==============================================================================
#==============================================================================
