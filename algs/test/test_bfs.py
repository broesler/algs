#!/usr/bin/env python3
#==============================================================================
#     File: bfs_test.py
#  Created: 2019-03-03 23:31
#   Author: Bernie Roesler
#
"""
  Description: Test BFS
"""
#==============================================================================

import re
import basics.graph as graph

pat = re.compile('(\d+)\s+(\d+)')
def parse(line):
    match = pat.search(line)
    return int(match.group(1)), int(match.group(2))

# Load test file
# filename = 'test_data/tinyDG.txt'
filename = 'test_data/tinyDAG.txt'
# filename = 'test_data/mediumDG.txt'

G = graph.Digraph()
with open(filename, 'r') as file:
    for i, line in enumerate(file.readlines()):
        if i < 2: continue
        a, b = parse(line)
        G.add_edge(a, b)

# Test BFS
s = G.roots()[0]  # get the first source
bfs = graph.BFSPaths(G, [s])
print('Unordered BFS:')
print('--------------')
bfs.print_paths()

# Test Ordered BFS
bfs_o = graph.BFSPaths(G, [s], ordered=True)
print('Ordered BFS:')
print('------------')
bfs_o.print_paths()

#==============================================================================
#==============================================================================
