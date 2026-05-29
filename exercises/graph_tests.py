#!/usr/bin/env python3
# ==============================================================================
#     File: test_graph.py
#  Created: 2019-03-03 23:31
#   Author: Bernie Roesler
# ==============================================================================

"""Test graph data structures."""

from pathlib import Path

from algs.graph.directed import Topological
from algs.graph.edgeweighted import (
    AcyclicPath,
    BreadthFirstSearch,
    DepthFirstOrder,
    DepthFirstSearch,
    Digraph,
    DirectedCycle,
)

DATA_PATH = Path(__file__).parent.parent / 'data'


def load_graph(filename):
    """Load a graph from a file."""
    G = Digraph()
    with Path(filename).open() as file:
        for i, line in enumerate(file.readlines()):
            if i == 0:
                V = int(line.rstrip())
            if i == 1:
                E = int(line.rstrip())
            if i < 2:
                continue
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
G = load_graph(DATA_PATH / 'tinyDG.txt')
# G = load_graph(DATA_PATH / 'mediumDG.txt')

sources = G.roots()
# assert s == 7  # only for tinyDG.txt

Gr = G.reverse()
for s in sources:
    assert Gr[s] == []  # source has no adjacents in reverse

# Test DFS
dfs = DepthFirstSearch(G, [sources[0]])
assert dfs.has_path_to(12)
assert str(dfs.path_to(12)) == str([7, 9, 10, 12])
print(f'{sources[0]} -> 12: ', dfs.path_to(12))

# Test paths
dfo = DepthFirstOrder(G)

finder = DirectedCycle(G)
assert finder.has_cycle

print('pre-order:      ', dfo.preorder)
print('post-order:     ', dfo.postorder)
print('rev-post-order: ', dfo.reverse_post)

# Test BFS
bfs = BreadthFirstSearch(G, [s])
# print('------------ Unordered BFS: ------------')
# bfs.print_paths()

# # Test Ordered BFS
bfs_o = BreadthFirstSearch(G, [s], ordered=True)
# print('------------ Ordered BFS: ------------')
# bfs_o.print_paths()

# Test Topological
DAG = load_graph(DATA_PATH / 'tinyDAG.txt')
topo = Topological(DAG)
assert topo
print('order: ', topo)

# Test EWD
EG = load_graph(DATA_PATH / 'tinyEWDAG.txt')
s = EG.roots()
assert len(s) == 1
ap = AcyclicPath(EG, s[0], kind='max')
print('----- Max Edge-Weighted DAG -----')
ap.print_paths()
assert ap.dist_to(s[0]) == 0.0

ap = AcyclicPath(EG, s[0], kind='min')
print('----- Min Edge-Weighted DAG -----')
ap.print_paths()
assert ap.dist_to(s[0]) == 0.0

# ==============================================================================
# ==============================================================================
