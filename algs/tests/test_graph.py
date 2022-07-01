#!/usr/bin/env python3
# =============================================================================
#     File: test_graph.py
#  Created: 2022-06-30 16:06
#   Author: Bernie Roesler
#
"""
  Description:
"""
# =============================================================================

import pytest

from algs.graph.undirected import (Graph, SimpleGraph,  STGraph, SymbolGraph,
                                   DepthFirstSearch, DepthFirstPaths,
                                   BreadthFirstPaths, DepthFirstPaths_nr,
                                   DepthFirstPaths_nr_simple, Cycle, CyclePath,
                                   CyclePath_nr, MinCyclePath, CC, CC_nr,
                                   UFSearch, LeafDFS, GraphProperties,
                                   Bipartite, Biconnected, ParallelEdges,
                                   spanning_tree_dfs, spanning_tree_bfs,
                                   spanning_forest_dfs, spanning_forest_bfs,
                                   print_adj, print_dfs, print_paths,
                                   print_components, degrees_of_separation)

# -----------------------------------------------------------------------------
#         Fixtures
# -----------------------------------------------------------------------------
# Expected values for tinyG
EXPECT_EDGES = tuple((
    (5, 3),
    (9, 11),
    (7, 8),
    (0, 6),
    (9, 10),
    (11, 12),
    (0, 2),
    (5, 4),
    (6, 4),
    (9, 12),
    (0, 1),
    (4, 3),
    (0, 5)
    ))

EXPECT_DEGREES = tuple((4, 1, 1, 2, 3, 3, 2, 1, 1, 3, 1, 2, 2))

EXPECT_ADJ = dict({
    0: [6, 2, 1, 5],
    1: [0],
    2: [0],
    3: [5, 4],
    4: [5, 6, 3],
    5: [3, 4, 0],
    6: [0, 4],
    7: [8],
    8: [7],
    9: [11, 10, 12],
    10: [9],
    11: [9, 12],
    12: [11, 9]
})


# Expected values for tinyCG
EXPECT_DFS = dict({
    0: [0],
    1: [0, 2, 1],
    2: [0, 2],
    3: [0, 2, 3],
    4: [0, 2, 3, 4],
    5: [0, 2, 3, 5],
})

EXPECT_DFS_S = dict({
    0: [0],
    1: [0, 5, 3, 2, 1],
    2: [0, 5, 3, 2],
    3: [0, 5, 3],
    4: [0, 5, 3, 2, 4],
    5: [0, 5],
})

EXPECT_BFS = dict({
    0: [0],
    1: [0, 1],
    2: [0, 2],
    3: [0, 2, 3],
    4: [0, 2, 4],
    5: [0, 5],
})


# NOTE paths are relative to where pytest is run from?
# See: <https://docs.pytest.org/en/6.2.x/customize.htmlinding-the-rootdir>
@pytest.fixture
def tinyCG(GT):
    return GT.fromfile('./data/tinyCG.txt')


@pytest.fixture
def tinyG(GT):
    return GT.fromfile('./data/tinyG.txt')


@pytest.fixture
def tinyG2(GT):
    return GT.fromfile('./data/tinyG2.txt')


# -----------------------------------------------------------------------------
#         Tests
# -----------------------------------------------------------------------------
@pytest.mark.parametrize('GT', [Graph, SimpleGraph, STGraph])
class TestTinyG:
    def test_constructor(self, GT):
        V = 13
        G = GT(V)
        assert list(G.vertices()) == list(range(G.V))
        for v, w in EXPECT_EDGES:
            G.add_edge(v, w)
            assert G.has_edge(v, w)
            assert G.has_edge(w, v)
        assert G.E == 13

    def test_fromfile(self, tinyG):
        assert tinyG.V == 13
        assert tinyG.E == 13
        for v, w in EXPECT_EDGES:
            assert tinyG.has_edge(v, w)
            assert tinyG.has_edge(w, v)
        assert list(tinyG.vertices()) == list(range(tinyG.V))

    def test_adj(self, tinyG):
        for v in tinyG.vertices():
            assert list(tinyG.adj(v)) == EXPECT_ADJ[v]

    def test_degrees(self, tinyG):
        for v in tinyG.vertices():
            assert tinyG.degree(v) == EXPECT_DEGREES[v]

    def test_validate_vertex(self, tinyG):
        with pytest.raises(IndexError):
            tinyG._validate_vertex(-1)
        with pytest.raises(IndexError):
            tinyG._validate_vertex(99)


# NOTE STGraph tests pass, but only because vertices are a range of integers
@pytest.mark.parametrize('GT', [Graph, SimpleGraph, STGraph])
@pytest.mark.parametrize('GraphSearch', [DepthFirstSearch, UFSearch])
class TestDFS:
    def test_dfs_CG(self, tinyCG, GraphSearch):
        dfs = GraphSearch(tinyCG, 0)
        assert dfs.count() == tinyCG.V
        assert all([dfs.marked(v) for v in tinyCG.vertices()])

    def test_dfs_G(self, tinyG, GraphSearch):
        dfs = GraphSearch(tinyG, 0)
        assert dfs.count() == 7
        assert all([dfs.marked(v) for v in range(6)])
        dfs = GraphSearch(tinyG, 7)
        assert dfs.count() == 2
        assert all([dfs.marked(v) for v in [7, 8]])
        dfs = GraphSearch(tinyG, 9)
        assert dfs.count() == 4
        assert all([dfs.marked(v) for v in [9, 10, 11, 12]])


@pytest.mark.parametrize('GT', [Graph, SimpleGraph, STGraph])
class TestPaths:
    @pytest.mark.parametrize('GraphSearch', [DepthFirstPaths,
                                             DepthFirstPaths_nr,
                                             DepthFirstPaths_nr_simple,
                                             BreadthFirstPaths])
    class TestHasPath:
        def test_has_path_to(self, tinyCG, GraphSearch):
            dfs = GraphSearch(tinyCG, 0)
            for v in tinyCG.vertices():
                assert dfs.has_path_to(v)

        def test_no_path_to(self, tinyG, GraphSearch):
            dfs = GraphSearch(tinyG, 0)
            for v in range(7):
                assert dfs.has_path_to(v)
            for v in range(7, tinyG.V):
                assert not dfs.has_path_to(v)

    @pytest.mark.parametrize('DFS, EXPECT', [(DepthFirstPaths, EXPECT_DFS),
                                             (DepthFirstPaths_nr, EXPECT_DFS),
                                             (DepthFirstPaths_nr_simple, EXPECT_DFS_S)])
    def test_dfs_path_to(self, tinyCG, DFS, EXPECT):
        dfs = DFS(tinyCG, 0)
        for v in tinyCG.vertices():
            assert list(dfs.path_to(v)) == EXPECT[v]

    def test_bfs_path_to(self, tinyCG):
        bfs = BreadthFirstPaths(tinyCG, 0)
        for v in tinyCG.vertices():
            assert list(bfs.path_to(v)) == EXPECT_BFS[v]
        assert [bfs.dist_to(v) for v in tinyCG.vertices()] == [0, 1, 1, 2, 2, 1]

    def test_leaf_CG(self, tinyCG):
        dfs = LeafDFS(tinyCG, 0)
        assert dfs.leaf() == 1  # returns first leaft

    def test_leaf_G(self, tinyG):
        dfs = LeafDFS(tinyG, 0)
        assert dfs.leaf() == 3  # returns first leaft

    def test_spanning_tree_dfs(self, tinyCG):
        EXPECT_ST = dict({
            0: [2],
            1: [2],
            2: [0, 1, 3],
            3: [2, 5, 4],
            4: [3],
            5: [3]
        })
        T = spanning_tree_dfs(tinyCG, 0)
        assert T.V == tinyCG.V
        assert T.E == tinyCG.V - 1  # minimum edges in connected graph
        assert list(T.vertices()) == list(tinyCG.vertices())
        for v in T.vertices():
            assert list(T.adj(v)) == EXPECT_ST[v]

    def test_spanning_tree_bfs(self, tinyCG):
        EXPECT_ST = dict({
            0: [2, 1, 5],
            1: [0],
            2: [0, 3, 4],
            3: [2],
            4: [2],
            5: [0]
        })
        T = spanning_tree_bfs(tinyCG, 0)
        assert T.V == tinyCG.V
        assert T.E == tinyCG.V - 1  # minimum edges in connected graph
        assert list(T.vertices()) == list(tinyCG.vertices())
        for v in T.vertices():
            assert list(T.adj(v)) == EXPECT_ST[v]

    def test_spanning_forest_dfs(self, tinyG):
        EXPECT_ST_0 = dict({
            0: [6, 2, 1],
            1: [0],
            2: [0],
            3: [5],
            4: [6, 5],
            5: [4, 3],
            6: [0, 4]
        })
        EXPECT_ST_1 = dict({7: [8], 8: [7]})
        EXPECT_ST_2 = dict({9: [11, 10], 10: [9], 11: [9, 12], 12: [11]})
        Ts = spanning_forest_dfs(tinyG)
        for T, expect in zip(Ts, [EXPECT_ST_0, EXPECT_ST_1, EXPECT_ST_2]):
            for v in expect:
                assert list(T.adj(v)) == expect[v]




# @pytest.mark.parametrize('ConComps', [CC, CC_nr])
# class TestCC:


# class TestBFSPaths:


# G = Graph.fromfile('../data/tinyG.txt')
# G2 = Graph.fromfile('../data/tinyG2.txt')

# # Test search
# print('----- DFS -----')
# print_dfs(G, 0)
# print_dfs(G, 9)

# # Test paths
# print('----- Connected Graph -----')
# G = Graph.fromfile('../data/tinyCG.txt')
# print(G)
# print_dfs(G, 0)
# print('----- DFS Paths -----')
# print_paths(G, 0, GS=DepthFirstPaths)

# G2 = Graph.fromfile('../data/tinyG2.txt')
# print('          G2:', DepthFirstPaths(G2, 0).path_to(10))
# print('       G2_nr:', DepthFirstPaths_nr(G2, 0).path_to(10))
# print('G2_nr_simple:', DepthFirstPaths_nr_simple(G2, 0).path_to(10))
# assert (DepthFirstPaths(G2, 0).path_to(10)
#         == DepthFirstPaths_nr(G2, 0).path_to(10))

# print('----- BFS Paths -----')
# print_paths(G, 0, GS=BreadthFirstPaths)

# # print('--- Cycle ---')
# G = Graph.fromfile('../data/tinyG.txt')
# c = CyclePath(G, 0)
# assert c.has_cycle
# assert c.cycle_path() == CyclePath_nr(G, 0).cycle_path()
# assert list(c.cycle_path()) == [3, 5, 4, 3]

# G2 = Graph.fromfile('../data/tinyG2.txt')
# c2 = CyclePath(G2, 0)
# assert c2.has_cycle
# assert list(c2.cycle_path()) == [2, 0, 6, 3, 2]

# # Test connected components
# print('----- CC -----')
# comps = print_components(G2)
# comps20 = print_components(G2, vertices=comps[0])

# # Test connected components
# print('----- SymbolGraph -----')
# sg = SymbolGraph.fromfile('../data/routes.txt')
# print('--- adjacency lists ---')
# print_adj(sg, 'JFK')
# print_adj(sg, 'LAX')
# print('--- shortest paths ---')
# degrees_of_separation(sg, 'JFK', 'LAS')
# degrees_of_separation(sg, 'JFK', 'DFW')

# # sg = SymbolGraph.fromfile('../data/movies.txt', delim='/')
# # print('--- adjacency lists ---')
# # print_adj(sg, 'Top Gun (1986)')
# # print('--- shortest paths ---')
# # degrees_of_separation(sg, 'Animal House (1978)', 'Titanic (1997)')
# # degrees_of_separation(sg, 'Bacon, Kevin', 'Cruise, Tom')

# # Test dist_to
# G = Graph.fromfile('../data/tinyG2.txt')
# bfs = BreadthFirstPaths(G, 0)
# assert ([bfs.dist_to(x) for x in G.vertices()]
#         == [0, None, 1, 2, None, 1, 1, None, None, None, 2, None])

# # Test copy
# Gc = G.copy()
# for v in G.vertices():
#     assert G.adj(v) == Gc.adj(v)
#     assert G._adj[v] is not Gc._adj[v]

# # Test has_edge
# assert G.has_edge(0, 5)
# assert G.has_edge(8, 1)
# assert not G.has_edge(0, 8)

# # Test no parallel edges
# G2 = Graph.fromfile('../data/tinyG2.txt', parallel=False)
# G2.add_edge(0, 2)
# assert G2.adj(0) == G.adj(0)  # no changes made
# G2.add_edge(0, 9)
# assert G2.adj(0) != G.adj(0)  # changes made

# # Test no self-edges
# try:
#     G.add_edge(9, 9)
# except ValueError:
#     pass

# # Test UF search
# ufs = UFSearch(G, 0)
# assert all([ufs.marked(x) for x in [2, 3, 5, 6, 10]])
# assert ufs.count() == 6  # number of vertices in source component

# # Test leaf finding
# lfs = LeafDFS(G, 0)
# assert lfs.leaf() == 10

# # Test properties
# try:
#     gp = GraphProperties(G)
# except ValueError:
#     pass

# print('----- Graph Properties -----')
# # gc = Graph.fromfile('../data/tinyCG.txt')
# gc = Graph.fromfile('../data/mediumG.txt')
# # NOTE maximum recursion depth reached in largeG!
# # gc = Graph.fromfile('../data/largeG.txt', verbose=True)

# gp = GraphProperties(gc)
# print('        ϵ:', gp.eccentricity(0))
# print(' diameter:', gp.diameter())
# print('   radius:', gp.radius())
# print('   center:', gp.center())
# print('periphery:', gp.periphery())
# print('    girth:', gp.girth())
# assert gp.eccentricity(gp.center()[0]) == gp.radius()

# print('--- Cycles ---')
# c = Cycle(gc, 0)
# assert c.has_cycle
# assert c.has_self_loop
# assert c.has_parallel_edges
# c = MinCyclePath(gc, 0)
# print(c.cycle_path())

# for N in range(2, 10):
#     edges = list()
#     for i in range(N):
#         edges.append((i, (i + 1) % N))
#     Gcyc = Graph(N, edges)
#     assert GraphProperties(Gcyc).girth() == N

# c = MinCyclePath(Gcyc, 0)
# print(c.cycle_path())

# G2 = Graph.fromfile('../data/tinyG2.txt')
# c2 = CC(G2)
# c2_nr = CC_nr(G2)
# comps2 = c2.get_components()
# assert comps2 == c2_nr.get_components()
# gp = GraphProperties(G2, comps2[0])
# idx = comps2[0][0]
# print(f"     ϵ({idx}): {gp.eccentricity(idx)}")
# print(' diameter:', gp.diameter())
# print('   radius:', gp.radius())
# print('   center:', gp.center())
# print('periphery:', gp.periphery())
# print('    girth:', gp.girth())

# b = Bipartite(G2, 0)
# assert not b.is_bipartite

# # 3 co-linear nodes are bipartite
# assert Bipartite(Graph(3, [(0, 1), (1, 2)]), 0).is_bipartite

# # Parallel edges
# G2.add_edge(0, 2)
# G2.add_edge(2, 6)
# G2.add_edge(10, 3)
# p = ParallelEdges(G2, 0)
# assert p.count == 3

# # print('----- Bridges -----')
# G2 = Graph.fromfile('../data/tinyG2.txt')
# # G2.add_edge(5, 7)  # one bridge
# G2.add_edge(5, 9)  # two bridges
# G2.add_edge(9, 7)  # 9 is an articulation point
# b = Biconnected(G2)
# # assert b.Nbridges == 1
# # assert b.articulation(7)
# assert b.Nbridges == 2
# assert b.articulation(9)

# # Spanning Tree
# print('----- Spanning Tree -----')
# G2 = Graph.fromfile('../data/tinyG2.txt')
# print('--- DFS ---')
# Td = spanning_tree_dfs(G2, 0)
# print(Td)
# print('--- BFS ---')
# Tb = spanning_tree_bfs(G2, 0)
# print(Tb)
# print('--- DFS Forest ---')
# Tf = spanning_forest_dfs(G2)
# print(Tf)
# print('--- BFS Forest ---')
# Tf = spanning_forest_bfs(G2)
# print(Tf)


# =============================================================================
# =============================================================================
