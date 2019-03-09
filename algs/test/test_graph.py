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

from algs import (Stack, Queue, PriorityQueue,
                  Digraph, DepthFirstSearch, DepthFirstOrder, DirectedCycle,
                  TopologicalOrder, BreadthFirstSearch, AcyclicPath)

def load_graph(filename):
    G = Digraph()
    with open(filename, 'r') as file:
        for i, line in enumerate(file.readlines()):
            if i == 0: V = int(line.rstrip())
            if i == 1: E = int(line.rstrip())
            if i < 2: continue
            nums = line.rstrip().split()
            args = [int(nums[0]), int(nums[1])]
            if len(nums) == 3:
                args.append(float(nums[2]))
            G.add_edge(*args)
    assert G.V == V
    assert G.E == E
    return G

# Load test file
# TODO loop over all test files
G = load_graph('test_data/tinyDG.txt')
# G = load_graph('test_data/mediumDG.txt')

sources = G.roots()
# assert s == 7  # only for tinyDG.txt

Gr = G.reverse()
for s in sources:
    assert Gr[s] == list([])  # source has no adjacents in reverse

# Test DFS
dfs = DepthFirstSearch(G, [sources[0]])
assert dfs.has_path_to(12)
assert dfs.path_to(12) == Stack([7, 9, 10, 12])
print(f'{sources[0]} -> 12: ', dfs.path_to(12))

# Test paths
dfo = DepthFirstOrder(G)

finder = DirectedCycle(G)
assert finder.has_cycle

print('pre-order:      ', dfo.preorder)
print('post-order:     ', dfo.postorder)
print('rev-post-order: ', dfo.reverse_post)

# Test TopologicalOrder
G = load_graph('test_data/tinyDAG.txt')
topo = TopologicalOrder(G)
assert topo
print('order: ', topo)

# Test BFS
# bfs = BreadthFirstSearch(G, [s])
# print('Unordered BFS:')
# print('--------------')
# bfs.print_paths()
#
# # Test Ordered BFS
# bfs_o = BreadthFirstSearch(G, [s], ordered=True)
# print('Ordered BFS:')
# print('------------')
# bfs_o.print_paths()

# Test EWD
EG = load_graph('test_data/tinyEWDAG.txt')
s = EG.roots()
ap = AcyclicPath(EG, s[0], kind='max')

#==============================================================================
#==============================================================================
