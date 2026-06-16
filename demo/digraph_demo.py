#!/usr/bin/env python3
# =============================================================================
#     File: digraph_util.py
#  Created: 2026-06-12 22:01
#   Author: Bernie Roesler
# =============================================================================

"""Demo usage of directed graph implementations and algorithms."""

from pathlib import Path

from graph_util import print_paths

from algs.graph.directed import (
    Digraph,
    KosarajuSCC,
    SymbolDigraph,
    check_topological,
    depth_first_order,
    directed_cycle,
    eulerian_cycle,
    hamiltonian_path,
    topological_order,
)
from algs.graph.search import BreadthFirstSearch, DepthFirstSearch

DATA_PATH = Path(__file__).parents[1] / 'data'

print('----- Digraph -----')
G = Digraph.fromfile(DATA_PATH / 'tinyDG.txt')
print(G)
print('----- Reverse -----')
R = G.reverse()
print(R)

print('----- DepthFirstSearch -----')
dfs = DepthFirstSearch(G, 2)
print(' '.join(f"{v} " for v in G.vertices() if dfs.has_path_to(v)))
dfs = DepthFirstSearch(G, [1, 2, 6])
print(' '.join(f"{v} " for v in G.vertices() if dfs.has_path_to(v)))

print('----- BreadthFirstSearch -----')
bfs = BreadthFirstSearch(G, 2)
print(' '.join(f"{v} " for v in G.vertices() if bfs.has_path_to(v)))
bfs = BreadthFirstSearch(G, [1, 2, 6])
print(' '.join(f"{v} " for v in G.vertices() if bfs.has_path_to(v)))

print('----- DFS Paths -----')
print_paths(G, 0, GS=DepthFirstSearch)
print('----- BFS Paths -----')
print_paths(G, 0, GS=BreadthFirstSearch)

print('----- Cycle -----')
cyc = directed_cycle(G)
print(cyc)

print('----- Orders -----')
p = depth_first_order(G)
print(p.pre)
print(p.post)
print(p.reverse_post)
assert list(reversed(p.post)) == p.reverse_post

t = topological_order(G)
assert not t

sg = SymbolDigraph.fromfile(DATA_PATH / 'jobs.txt', delim='/')
t = topological_order(sg.graph)
assert t
print('\n'.join(sg.name_of(v) for v in t))

print('----- Strongly Connected Components -----')
cc = KosarajuSCC(G)
assert cc.count == 5
print(cc.get_components())

# Web Exercise 17
Gm = Digraph.fromfile(DATA_PATH / 'mediumDG.txt')
cc = KosarajuSCC(Gm)
assert cc.count == 10

G2 = Digraph.fromfile(DATA_PATH / 'tinyDG2.txt')
print(G2)
assert G2._indegree == [1, 2, 2, 2, 1, 0, 2, 0, 2, 0, 2, 2]
assert [G2.outdegree(v) for v in G2.vertices()] == [1, 1, 2, 2, 1, 2, 1, 2, 2, 0, 1, 1]
assert G2.sources == [5, 7, 9]
assert G2.sinks == [9]

# Exercise 4.2.20: Eulerican cycle: Create a circular graph
print('----- Eulerican Cycle -----')
edges = []
N = 5
Gcyc = Digraph(N)
for i in range(N):
    Gcyc.add_edge(i, (i + 1) % N)
e = eulerian_cycle(Gcyc)
print(e)

Gno_cyc = Digraph(N)
for i in range(N - 1):
    Gno_cyc.add_edge(i, i + 1)
e = eulerian_cycle(Gno_cyc)
assert not e

print('----- DAGs -----')
D = Digraph.fromfile(DATA_PATH / 'tinyDAG.txt')
print(D)
orders = depth_first_order(D)
print('   pre:', orders.pre)
print('  post:', orders.post)
print('r_post:', orders.reverse_post)
t = topological_order(D)
print('  topo:', t)
assert t == orders.reverse_post

assert check_topological(D, t)

cc = KosarajuSCC(D)
print(cc.get_components())

# Exercise 4.2.24: Hamiltonian path
print('----- Hamiltonian Path -----')
h = hamiltonian_path(Gno_cyc)
assert h == list(range(N))
print(h)

H = Digraph(N)
j = N // 2
for i in range(N - 1):
    if i == j:
        continue
    H.add_edge(i, i + 1)
H.add_edge(j + 1, j)
h = hamiltonian_path(H)
assert not h


# =============================================================================
# =============================================================================
