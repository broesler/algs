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

EXPECT_COMPS = [list(range(7)), [7, 8], [9, 10, 11, 12]]


# NOTE paths are relative to where pytest is run from?
# See: <https://docs.pytest.org/en/6.2.x/customize.htmlinding-the-rootdir>
@pytest.fixture
def tinyCG(GT):
    return GT.fromfile('./data/tinyCG.txt')


@pytest.fixture
def tinyG(GT):
    return GT.fromfile('./data/tinyG.txt')


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
        assert not G.has_edge(0, 7)
        assert G.E == 13

    def test_fromfile(self, tinyG):
        assert tinyG.V == 13
        assert tinyG.E == 13
        for v, w in EXPECT_EDGES:
            assert tinyG.has_edge(v, w)
            assert tinyG.has_edge(w, v)
        assert not tinyG.has_edge(0, 7)
        assert list(tinyG.vertices()) == list(range(tinyG.V))

    def test_adj(self, tinyG):
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
        for v in tinyG.vertices():
            assert list(tinyG.adj(v)) == EXPECT_ADJ[v]

    def test_degrees(self, tinyG):
        EXPECT_DEGREES = tuple((4, 1, 1, 2, 3, 3, 2, 1, 1, 3, 1, 2, 2))
        for v in tinyG.vertices():
            assert tinyG.degree(v) == EXPECT_DEGREES[v]

    def test_validate_vertex(self, tinyG):
        with pytest.raises(IndexError):
            tinyG._validate_vertex(-1)
        with pytest.raises(IndexError):
            tinyG._validate_vertex(99)

    def test_copy(self, tinyG):
        H = tinyG.copy()
        for v in tinyG.vertices():
            assert H.adj(v) == tinyG.adj(v)
            assert H._adj[v] is not tinyG._adj[v]


# Simple graph does not allow parallel edges or self-loops
@pytest.mark.parametrize('GT', [SimpleGraph])
class TestSimple:
    def test_self_loop(self, tinyG):
        with pytest.raises(ValueError):
            tinyG.add_edge(0, 0)

    def test_parallel_edges(self, tinyG):
        assert tinyG.degree(0) == 4
        assert tinyG.degree(1) == 1
        tinyG.add_edge(0, 1)
        # No changes
        assert tinyG.degree(0) == 4
        assert tinyG.degree(1) == 1


@pytest.mark.parametrize('GT', [Graph, STGraph])
class TestNonSimple:
    def test_self_loop(self, GT):
        G = GT.fromfile('./data/tinyG.txt', self_loops=True)
        G.add_edge(0, 0)
        assert G.has_edge(0, 0)

    def test_no_self_loop(self, GT):
        G = GT.fromfile('./data/tinyG.txt', self_loops=False)
        with pytest.raises(ValueError):
            G.add_edge(0, 0)

    def test_parallel_edges(self, GT):
        G = GT.fromfile('./data/tinyG.txt', parallel=True)
        assert G.degree(0) == 4
        assert G.degree(1) == 1
        G.add_edge(0, 1)
        assert G.degree(0) == 5
        assert G.degree(1) == 2

    def test_no_parallel_edges(self, GT):
        G = GT.fromfile('./data/tinyG.txt', parallel=False)
        assert G.degree(0) == 4
        assert G.degree(1) == 1
        G.add_edge(0, 1)
        assert G.degree(0) == 4
        assert G.degree(1) == 1


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

    def test_spanning_forest_bfs(self, tinyG):
        EXPECT_ST_0 = dict({
            0: [6, 2, 1, 5],
            1: [0],
            2: [0],
            3: [5],
            4: [6],
            5: [0, 3],
            6: [0, 4],
        })
        EXPECT_ST_1 = dict({7: [8], 8: [7]})
        EXPECT_ST_2 = dict({9: [11, 10, 12], 10: [9], 11: [9], 12: [9]})
        Ts = spanning_forest_bfs(tinyG)
        for T, expect in zip(Ts, [EXPECT_ST_0, EXPECT_ST_1, EXPECT_ST_2]):
            for v in expect:
                assert list(T.adj(v)) == expect[v]


@pytest.mark.parametrize('GT', [Graph, SimpleGraph, STGraph])
@pytest.mark.parametrize('ConComps', [CC, CC_nr])
class TestCC:
    @pytest.mark.parametrize('G, expect', [('tinyG', False), ('tinyCG', True)])
    def test_is_connected(self, ConComps, GT, G, expect, request):
        cc = ConComps(request.getfixturevalue(G))
        assert cc.is_connected == expect

    def test_count(self, ConComps, tinyG):
        cc = ConComps(tinyG)
        assert cc.count() == 3

    def test_connected(self, ConComps, tinyG):
        cc = ConComps(tinyG)
        for comp in EXPECT_COMPS:
            for i in range(len(comp)):
                for j in range(i, len(comp)):
                    assert cc.connected(comp[i], comp[j])

    def test_id(self, ConComps, tinyG):
        cc = ConComps(tinyG)
        for i, comp in enumerate(EXPECT_COMPS):
            for c in comp:
                assert cc.id(c) == i

    def test_get_components(self, ConComps, tinyG):
        cc = ConComps(tinyG)
        comps = cc.get_components()
        for i, comp in enumerate(EXPECT_COMPS):
            assert comps[i] == comp

    def test_cc_vs(self, ConComps, tinyG):
        cc = ConComps(tinyG, vertices=range(9))
        comps = cc.get_components()
        assert cc.count() == 2
        for i, comp in enumerate(EXPECT_COMPS[:2]):
            assert comps[i] == comp


# @pytest.mark.parametrize('GT', [Graph, SimpleGraph, STGraph])
# class TestCycle:




# =============================================================================
# =============================================================================
