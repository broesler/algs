#!/usr/bin/env python3
# =============================================================================
#     File: test_undirected.py
#  Created: 2022-06-30 16:06
#   Author: Bernie Roesler
# =============================================================================

"""Tests for undirected graph algorithms."""

import pytest

from algs.graph.search import (
    BreadthFirstSearch,
    DepthFirstSearch,
    DepthFirstSearch_nr,
    DepthFirstSearch_nr_simple,
)
from algs.graph.undirected import (
    CC,
    Biconnected,
    CC_nr,
    Graph,
    GraphProperties,
    SimpleGraph,
    SymbolGraph,
    UFSearch,
    bipartite_colors,
    find_cycle_path,
    find_min_cycle,
    has_cycle,
    spanning_forest_bfs,
    spanning_forest_dfs,
    spanning_tree_bfs,
    spanning_tree_dfs,
)


# -----------------------------------------------------------------------------
#         Fixtures
# -----------------------------------------------------------------------------
@pytest.fixture
def tinyCG(graph_type, data_dir):
    return graph_type.fromfile(data_dir / 'tinyCG.txt')


@pytest.fixture
def tinyG(graph_type, data_dir):
    return graph_type.fromfile(data_dir / 'tinyG.txt')


@pytest.fixture
def sg(data_dir):
    return SymbolGraph.fromfile(data_dir / 'routes.txt')


@pytest.fixture
def cc(ConComps, tinyG, graph_type):
    return ConComps(tinyG)


# TODO come up with more interesting graph for GraphProperties that has
# different values for eccentricities, diameter, radius, etc.
@pytest.fixture
def nonogon(graph_type):
    V = 9
    G = graph_type(V)
    for i in range(V):
        G.add_edge(i, (i + 1) % V)
    return G


@pytest.fixture
def gp(graph_type, nonogon):
    return GraphProperties(nonogon)


EXPECT_DFS = {
    0: [0],
    1: [0, 2, 1],
    2: [0, 2],
    3: [0, 2, 3],
    4: [0, 2, 3, 4],
    5: [0, 2, 3, 5],
}

# Expected values for tinyCG
EXPECT_DFS_S = {
    0: [0],
    1: [0, 5, 3, 2, 1],
    2: [0, 5, 3, 2],
    3: [0, 5, 3],
    4: [0, 5, 3, 2, 4],
    5: [0, 5],
}


@pytest.fixture
def acyclicG(graph_type):
    V = 5
    G = graph_type(V)
    for i in range(V - 1):
        G.add_edge(i, i + 1)
    return G


# -----------------------------------------------------------------------------
#         Tests
# -----------------------------------------------------------------------------
@pytest.mark.parametrize('graph_type', [Graph, SimpleGraph])
class TestTinyG:
    @pytest.fixture(scope='class')
    @staticmethod
    def expect_tinyG_edges():
        return (
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
            (0, 5),
        )

    def test_constructor(self, graph_type, expect_tinyG_edges):
        V = 13
        G = graph_type(V)
        assert list(G.vertices()) == list(range(G.V))
        for v, w in expect_tinyG_edges:
            G.add_edge(v, w)
            assert G.has_edge(v, w)
            assert G.has_edge(w, v)
        assert not G.has_edge(0, 7)
        assert G.E == 13

    def test_fromfile(self, tinyG, expect_tinyG_edges):
        assert tinyG.V == 13
        assert tinyG.E == 13
        for v, w in expect_tinyG_edges:
            assert tinyG.has_edge(v, w)
            assert tinyG.has_edge(w, v)
        assert not tinyG.has_edge(0, 7)
        assert list(tinyG.vertices()) == list(range(tinyG.V))

    def test_adj(self, tinyG):
        expect_adj = {
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
            12: [11, 9],
        }

        for v in tinyG.vertices():
            assert list(tinyG.adj(v)) == expect_adj[v]

    def test_degrees(self, tinyG):
        expect_degrees = (4, 1, 1, 2, 3, 3, 2, 1, 1, 3, 1, 2, 2)
        for v in tinyG.vertices():
            assert tinyG.degree(v) == expect_degrees[v]
        assert tinyG.max_degree == max(expect_degrees)
        assert tinyG.avg_degree == pytest.approx(
            sum(expect_degrees) / len(expect_degrees)
        )

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
@pytest.mark.parametrize('graph_type', [SimpleGraph])
class TestSimple:
    def test_self_loop(self, tinyG):
        with pytest.raises(ValueError):
            tinyG.add_edge(0, 0)
        assert tinyG.num_self_loops == 0

    def test_parallel_edges(self, tinyG):
        assert tinyG.degree(0) == 4
        assert tinyG.degree(1) == 1
        tinyG.add_edge(0, 1)
        # No changes
        assert tinyG.degree(0) == 4
        assert tinyG.degree(1) == 1


class TestNonSimple:
    @pytest.fixture
    @staticmethod
    def make_tinyG(data_dir):
        def _make_tinyG(**kwargs):
            return Graph.fromfile(data_dir / 'tinyG.txt', **kwargs)

        return _make_tinyG

    def test_no_self_loops(self, make_tinyG):
        G = make_tinyG(self_loops=False)
        assert not G.has_self_loop
        with pytest.raises(ValueError):
            G.add_edge(0, 0)

    def test_self_loops(self, make_tinyG):
        G = make_tinyG(self_loops=True)
        assert not G.has_self_loop
        assert G.num_self_loops == 0
        G.add_edge(1, 1)
        assert G.has_self_loop
        assert G.num_self_loops == 1
        G.add_edge(1, 1)
        G.add_edge(1, 1)
        G.add_edge(9, 9)
        assert G.num_self_loops == 4

    def test_no_parallel_edges(self, make_tinyG):
        G = make_tinyG(parallel=False)
        assert not G.has_parallel_edges
        assert G.num_parallel_edges == 0
        G.add_edge(0, 1)
        assert not G.has_parallel_edges
        assert G.num_parallel_edges == 0

    def test_parallel_edges(self, make_tinyG):
        G = make_tinyG(parallel=True)
        assert not G.has_parallel_edges
        G.add_edge(0, 1)
        assert G.has_parallel_edges
        assert G.num_parallel_edges == 1
        G.add_edge(0, 2)
        assert G.has_parallel_edges
        assert G.num_parallel_edges == 2


# TODO expect_edges
# Test has_edge, add_edge, index, name, contains
class TestSymbolGraph:
    def test_adj(self, sg):
        EXPECT = ['MCO', 'ATL', 'ORD']
        assert sg.adj('JFK') == EXPECT


@pytest.mark.parametrize('graph_type', [Graph, SimpleGraph])
class TestSpanningTrees:
    def test_spanning_tree_dfs(self, tinyCG):
        expect_st = {0: [2], 1: [2], 2: [0, 1, 3], 3: [2, 5, 4], 4: [3], 5: [3]}
        T = spanning_tree_dfs(tinyCG, 0)
        assert T.V == tinyCG.V
        assert T.E == tinyCG.V - 1  # minimum edges in connected graph
        assert list(T.vertices()) == list(tinyCG.vertices())
        for v in T.vertices():
            assert list(T.adj(v)) == expect_st[v]

    def test_spanning_tree_bfs(self, tinyCG):
        expect_st = {0: [2, 1, 5], 1: [0], 2: [0, 3, 4], 3: [2], 4: [2], 5: [0]}
        T = spanning_tree_bfs(tinyCG, 0)
        assert T.V == tinyCG.V
        assert T.E == tinyCG.V - 1  # minimum edges in connected graph
        assert list(T.vertices()) == list(tinyCG.vertices())
        for v in T.vertices():
            assert list(T.adj(v)) == expect_st[v]

    def test_spanning_forest_dfs(self, tinyG):
        expect_st_0 = {
            0: [6, 2, 1],
            1: [0],
            2: [0],
            3: [5],
            4: [6, 5],
            5: [4, 3],
            6: [0, 4],
        }
        expect_st_1 = {7: [8], 8: [7]}
        expect_st_2 = {9: [11, 10], 10: [9], 11: [9, 12], 12: [11]}
        Ts = spanning_forest_dfs(tinyG)
        for T, expect in zip(Ts, [expect_st_0, expect_st_1, expect_st_2]):
            for v in expect:
                assert list(T.adj(v)) == expect[v]

    def test_spanning_forest_bfs(self, tinyG):
        expect_st_0 = {
            0: [6, 2, 1, 5],
            1: [0],
            2: [0],
            3: [5],
            4: [6],
            5: [0, 3],
            6: [0, 4],
        }
        expect_st_1 = {7: [8], 8: [7]}
        expect_st_2 = {9: [11, 10, 12], 10: [9], 11: [9], 12: [9]}
        Ts = spanning_forest_bfs(tinyG)
        for T, expect in zip(Ts, [expect_st_0, expect_st_1, expect_st_2]):
            for v in expect:
                assert list(T.adj(v)) == expect[v]


@pytest.mark.parametrize('graph_type', [Graph, SimpleGraph])
@pytest.mark.parametrize('ConComps', [CC, CC_nr])
class TestCC:
    @pytest.fixture(scope='class')
    @staticmethod
    def expect_comps():
        return [list(range(7)), [7, 8], [9, 10, 11, 12]]

    def test_is_connected(self, ConComps, tinyG, tinyCG):
        cc = ConComps(tinyG)
        assert not cc.is_connected
        cc = ConComps(tinyCG)
        assert cc.is_connected

    def test_count(self, ConComps, tinyG):
        cc = ConComps(tinyG)
        assert cc.count == 3

    def test_connected(self, cc, expect_comps):
        for comp in expect_comps:
            for i in range(len(comp)):
                for j in range(i, len(comp)):
                    assert cc.connected(comp[i], comp[j])

    def test_id(self, cc, expect_comps):
        for i, comp in enumerate(expect_comps):
            for c in comp:
                assert cc.id(c) == i

    def test_get_components(self, cc, expect_comps):
        comps = cc.get_components()
        for i, comp in enumerate(expect_comps):
            assert comps[i] == comp

    def test_cc_vs(self, ConComps, tinyG, expect_comps):
        cc = ConComps(tinyG, vertices=range(9))
        comps = cc.get_components()
        assert cc.count == 2
        for i, comp in enumerate(expect_comps[:2]):
            assert comps[i] == comp


@pytest.mark.parametrize('graph_type', [Graph, SimpleGraph])
class TestBipartite:
    def test_not_bipartite(self, tinyG):
        b = bipartite_colors(tinyG)
        assert not b.colors

    def test_is_bipartite(self, tinyG):
        # Tweak tinyG to make it bipartite
        tinyG.add_edge(1, 3)
        tinyG.add_edge(6, 7)
        tinyG.add_edge(8, 10)
        tinyG.add_edge(10, 12)
        # Remove edges (inside hack to Bag's _items list)
        tinyG._adj[3]._items.remove(4)
        tinyG._adj[4]._items.remove(3)
        tinyG._adj[9]._items.remove(12)
        tinyG._adj[12]._items.remove(9)
        b = bipartite_colors(tinyG)
        assert b.colors


@pytest.mark.parametrize('graph_type', [Graph, SimpleGraph])
class TestBiconnected:
    def test_not_biconnected(self, tinyG):
        b = Biconnected(tinyG)
        assert not b.is_edge_connected
        assert b.Nbridges == 4
        assert all(b.articulation(v) for v in [0, 9])

    def test_is_biconnected(self, tinyCG):
        b = Biconnected(tinyCG)
        assert b.is_edge_connected
        assert b.Nbridges == 0
        assert not any(b.articulation(v) for v in tinyCG.vertices())


# TODO test unconnected graph
@pytest.mark.parametrize('graph_type', [Graph, SimpleGraph])
class TestGraphProperties:
    def test_eccentricity(self, gp):
        assert gp.eccentricity(0) == 4

    def test_diameter(self, gp):
        assert gp.diameter() == 4

    def test_radius(self, gp):
        assert gp.radius() == 4

    def test_center(self, gp):
        assert gp.center() == list(range(9))

    def test_periphery(self, gp):
        assert gp.periphery() == list(range(9))

    def test_girth(self, gp):
        assert gp.girth() == 9

    def test_inf_girth(self, graph_type):
        G = graph_type(2, [(0, 1)])
        assert GraphProperties(G).girth() == float('inf')

    def test_girths(self, graph_type):
        # Generate a simple cycle graph
        for N in range(3, 10):
            edges = []
            for i in range(N):
                edges.append((i, (i + 1) % N))
            Gcyc = graph_type(N, edges)
            assert GraphProperties(Gcyc).girth() == N


# -----------------------------------------------------------------------------
#         Test Search
# -----------------------------------------------------------------------------
@pytest.mark.parametrize('graph_type', [Graph, SimpleGraph])
@pytest.mark.parametrize('GraphSearch', [DepthFirstSearch, UFSearch])
class TestDFS:
    def test_dfs_CG(self, tinyCG, GraphSearch):
        dfs = GraphSearch(tinyCG, 0)
        assert dfs.count == tinyCG.V
        assert all(dfs.has_path_to(v) for v in tinyCG.vertices())

    def test_dfs_G(self, tinyG, GraphSearch):
        dfs = GraphSearch(tinyG, 0)
        assert dfs.count == 7
        assert all(dfs.has_path_to(v) for v in range(6))
        dfs = GraphSearch(tinyG, 7)
        assert dfs.count == 2
        assert all(dfs.has_path_to(v) for v in [7, 8])
        dfs = GraphSearch(tinyG, 9)
        assert dfs.count == 4
        assert all(dfs.has_path_to(v) for v in [9, 10, 11, 12])


@pytest.mark.parametrize('graph_type', [Graph, SimpleGraph])
@pytest.mark.parametrize('recursive', [True, False])
def test_has_cycle(tinyG, acyclicG, recursive):
    assert has_cycle(tinyG, 0, recursive=recursive)
    assert not has_cycle(acyclicG, 0, recursive=recursive)


@pytest.mark.parametrize('graph_type', [Graph, SimpleGraph])
class TestPaths:
    @pytest.mark.parametrize(
        'GraphSearch',
        [
            DepthFirstSearch,
            DepthFirstSearch_nr,
            DepthFirstSearch_nr_simple,
            BreadthFirstSearch,
        ],
    )
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

    @pytest.mark.parametrize(
        'search_class, expected_paths',
        [
            (DepthFirstSearch, EXPECT_DFS),
            (DepthFirstSearch_nr, EXPECT_DFS),
            (DepthFirstSearch_nr_simple, EXPECT_DFS_S),
        ],
    )
    def test_dfs_path_to(self, tinyCG, search_class, expected_paths):
        dfs = search_class(tinyCG, 0)
        actual_paths = {v: list(dfs.path_to(v)) for v in tinyCG.vertices()}
        assert actual_paths == expected_paths

    def test_bfs_path_to(self, tinyCG):
        expect_paths = {
            0: [0],
            1: [0, 1],
            2: [0, 2],
            3: [0, 2, 3],
            4: [0, 2, 4],
            5: [0, 5],
        }
        bfs = BreadthFirstSearch(tinyCG, 0)
        actual_paths = {v: list(bfs.path_to(v)) for v in tinyCG.vertices()}
        assert actual_paths == expect_paths

    def test_bfs_dist_to(self, tinyCG):
        bfs = BreadthFirstSearch(tinyCG, 0)
        expect_dist_to = [0, 1, 1, 2, 2, 1]
        actual_dist_to = [bfs.dist_to(v) for v in tinyCG.vertices()]
        assert actual_dist_to == expect_dist_to

    @pytest.mark.parametrize('GraphSearch', [DepthFirstSearch, DepthFirstSearch_nr])
    def test_leaf_CG(self, GraphSearch, tinyCG):
        assert GraphSearch(tinyCG, 0).leaf == 1

    @pytest.mark.parametrize('GraphSearch', [DepthFirstSearch, DepthFirstSearch_nr])
    def test_leaf_G(self, GraphSearch, tinyG):
        assert GraphSearch(tinyG, 0).leaf == 3
        assert GraphSearch(tinyG, 6).leaf == 2
        assert GraphSearch(tinyG, 7).leaf == 8


@pytest.mark.parametrize('graph_type', [Graph, SimpleGraph])
class TestCyclePath:
    @pytest.mark.parametrize('recursive', [True, False])
    def test_cycle_path_dfs(self, recursive, tinyG):
        cyc = find_cycle_path(tinyG, 0, recursive=recursive)
        assert cyc == [3, 4, 5, 3]

    @pytest.mark.parametrize('recursive', [True, False])
    def test_no_cycle_path_dfs(self, recursive, acyclicG):
        cyc = find_cycle_path(acyclicG, 0, recursive=recursive)
        assert not cyc

    def test_cycle_path_bfs(self, tinyG, acyclicG):
        assert find_min_cycle(tinyG, 0) == [4, 6, 0, 5, 4]
        assert find_min_cycle(acyclicG, 0) == []


# =============================================================================
# =============================================================================
