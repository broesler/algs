#!/usr/bin/env python3
# =============================================================================
#     File: test_graph.py
#  Created: 2022-06-30 16:06
#   Author: Bernie Roesler
# =============================================================================

"""Tests for undirected graph algorithms."""

from pathlib import Path

import pytest

from algs.graph.undirected import (
    CC,
    Biconnected,
    CC_nr,
    Graph,
    GraphProperties,
    SimpleGraph,
    SymbolGraph,
    bipartite_colors,
    spanning_forest_bfs,
    spanning_forest_dfs,
    spanning_tree_bfs,
    spanning_tree_dfs,
)

# -----------------------------------------------------------------------------
#         Fixtures
# -----------------------------------------------------------------------------
EXPECT_EDGES = (
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

EXPECT_COMPS = [list(range(7)), [7, 8], [9, 10, 11, 12]]

DATA_DIR = Path(__file__).parents[2] / 'data'


@pytest.fixture
def sg():
    return SymbolGraph.fromfile(DATA_DIR / 'routes.txt')


@pytest.fixture
def cc(ConComps, tinyG, GraphType):
    return ConComps(tinyG)


# TODO come up with more interesting graph for GraphProperties that has
# different values for eccentricities, diameter, radius, etc.
@pytest.fixture
def nonogon(GraphType):
    V = 9
    G = GraphType(V)
    for i in range(V):
        G.add_edge(i, (i + 1) % V)
    return G


@pytest.fixture
def gp(GraphType, nonogon):
    return GraphProperties(nonogon)


# -----------------------------------------------------------------------------
#         Tests
# -----------------------------------------------------------------------------
@pytest.mark.parametrize('GraphType', [Graph, SimpleGraph])
class TestTinyG:
    def test_constructor(self, GraphType):
        V = 13
        G = GraphType(V)
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
        EXPECT_ADJ = {
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
            assert list(tinyG.adj(v)) == EXPECT_ADJ[v]

    def test_degrees(self, tinyG):
        EXPECT_DEGREES = (4, 1, 1, 2, 3, 3, 2, 1, 1, 3, 1, 2, 2)
        for v in tinyG.vertices():
            assert tinyG.degree(v) == EXPECT_DEGREES[v]
        assert tinyG.max_degree == max(EXPECT_DEGREES)
        assert tinyG.avg_degree == sum(EXPECT_DEGREES) / len(EXPECT_DEGREES)

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
@pytest.mark.parametrize('GraphType', [SimpleGraph])
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


@pytest.mark.parametrize('GraphType', [Graph])
class TestNonSimple:
    def test_self_loop(self, GraphType):
        G = GraphType.fromfile(DATA_DIR / 'tinyG.txt', self_loops=True)
        G.add_edge(0, 0)
        assert G.has_edge(0, 0)

    def test_no_self_loop(self, GraphType):
        G = GraphType.fromfile(DATA_DIR / 'tinyG.txt', self_loops=False)
        with pytest.raises(ValueError):
            G.add_edge(0, 0)

    def test_parallel_edges(self, GraphType):
        G = GraphType.fromfile(DATA_DIR / 'tinyG.txt', parallel=True)
        assert G.degree(0) == 4
        assert G.degree(1) == 1
        assert G.num_parallel_edges == 0
        G.add_edge(0, 1)
        assert G.degree(0) == 5
        assert G.degree(1) == 2
        assert G.num_parallel_edges == 1

    def test_no_parallel_edges(self, GraphType):
        G = GraphType.fromfile(DATA_DIR / 'tinyG.txt', parallel=False)
        assert G.degree(0) == 4
        assert G.degree(1) == 1
        assert G.num_parallel_edges == 0
        G.add_edge(0, 1)
        assert G.degree(0) == 4
        assert G.degree(1) == 1
        assert G.num_parallel_edges == 0


# TODO expect_edges
# Test has_edge, add_edge, index, name, contains
class TestSymbolGraph:
    def test_adj(self, sg):
        EXPECT = ['MCO', 'ATL', 'ORD']
        assert sg.adj('JFK') == EXPECT


@pytest.mark.parametrize('GraphType', [Graph, SimpleGraph])
class TestSpanningTrees:
    def test_spanning_tree_dfs(self, tinyCG):
        EXPECT_ST = {0: [2], 1: [2], 2: [0, 1, 3], 3: [2, 5, 4], 4: [3], 5: [3]}
        T = spanning_tree_dfs(tinyCG, 0)
        assert T.V == tinyCG.V
        assert T.E == tinyCG.V - 1  # minimum edges in connected graph
        assert list(T.vertices()) == list(tinyCG.vertices())
        for v in T.vertices():
            assert list(T.adj(v)) == EXPECT_ST[v]

    def test_spanning_tree_bfs(self, tinyCG):
        EXPECT_ST = {0: [2, 1, 5], 1: [0], 2: [0, 3, 4], 3: [2], 4: [2], 5: [0]}
        T = spanning_tree_bfs(tinyCG, 0)
        assert T.V == tinyCG.V
        assert T.E == tinyCG.V - 1  # minimum edges in connected graph
        assert list(T.vertices()) == list(tinyCG.vertices())
        for v in T.vertices():
            assert list(T.adj(v)) == EXPECT_ST[v]

    def test_spanning_forest_dfs(self, tinyG):
        EXPECT_ST_0 = {
            0: [6, 2, 1],
            1: [0],
            2: [0],
            3: [5],
            4: [6, 5],
            5: [4, 3],
            6: [0, 4],
        }
        EXPECT_ST_1 = {7: [8], 8: [7]}
        EXPECT_ST_2 = {9: [11, 10], 10: [9], 11: [9, 12], 12: [11]}
        Ts = spanning_forest_dfs(tinyG)
        for T, expect in zip(Ts, [EXPECT_ST_0, EXPECT_ST_1, EXPECT_ST_2]):
            for v in expect:
                assert list(T.adj(v)) == expect[v]

    def test_spanning_forest_bfs(self, tinyG):
        EXPECT_ST_0 = {
            0: [6, 2, 1, 5],
            1: [0],
            2: [0],
            3: [5],
            4: [6],
            5: [0, 3],
            6: [0, 4],
        }
        EXPECT_ST_1 = {7: [8], 8: [7]}
        EXPECT_ST_2 = {9: [11, 10, 12], 10: [9], 11: [9], 12: [9]}
        Ts = spanning_forest_bfs(tinyG)
        for T, expect in zip(Ts, [EXPECT_ST_0, EXPECT_ST_1, EXPECT_ST_2]):
            for v in expect:
                assert list(T.adj(v)) == expect[v]


@pytest.mark.parametrize('GraphType', [Graph, SimpleGraph])
@pytest.mark.parametrize('ConComps', [CC, CC_nr])
class TestCC:
    def test_is_connected(self, ConComps, tinyG, tinyCG):
        cc = ConComps(tinyG)
        assert not cc.is_connected
        cc = ConComps(tinyCG)
        assert cc.is_connected

    def test_count(self, ConComps, tinyG):
        cc = ConComps(tinyG)
        assert cc.count() == 3

    def test_connected(self, cc):
        for comp in EXPECT_COMPS:
            for i in range(len(comp)):
                for j in range(i, len(comp)):
                    assert cc.connected(comp[i], comp[j])

    def test_id(self, cc):
        for i, comp in enumerate(EXPECT_COMPS):
            for c in comp:
                assert cc.id(c) == i

    def test_get_components(self, cc):
        comps = cc.get_components()
        for i, comp in enumerate(EXPECT_COMPS):
            assert comps[i] == comp

    def test_cc_vs(self, ConComps, tinyG):
        cc = ConComps(tinyG, vertices=range(9))
        comps = cc.get_components()
        assert cc.count() == 2
        for i, comp in enumerate(EXPECT_COMPS[:2]):
            assert comps[i] == comp


@pytest.mark.parametrize('GraphType', [Graph])
class TestCycle:
    def test_has_self_loop(self, tinyG):
        assert not tinyG.has_self_loop
        tinyG.add_edge(1, 1)
        assert tinyG.has_self_loop

    def test_num_self_loops(self, tinyG):
        assert tinyG.num_self_loops == 0
        tinyG.add_edge(1, 1)
        tinyG.add_edge(1, 1)
        tinyG.add_edge(9, 9)
        assert tinyG.num_self_loops == 3

    def test_has_parallel_edges(self, tinyG):
        assert not tinyG.has_parallel_edges
        tinyG.add_edge(0, 1)
        assert tinyG.has_parallel_edges
        assert tinyG.num_parallel_edges == 1
        tinyG.add_edge(0, 2)
        assert tinyG.has_parallel_edges
        assert tinyG.num_parallel_edges == 2


@pytest.mark.parametrize('GraphType', [Graph, SimpleGraph])
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


@pytest.mark.parametrize('GraphType', [Graph, SimpleGraph])
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
@pytest.mark.parametrize('GraphType', [Graph, SimpleGraph])
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

    def test_inf_girth(self, GraphType):
        G = GraphType(2, [(0, 1)])
        assert GraphProperties(G).girth() == float('inf')

    def test_girths(self, GraphType):
        # Generate a simple cycle graph
        for N in range(3, 10):
            edges = []
            for i in range(N):
                edges.append((i, (i + 1) % N))
            Gcyc = GraphType(N, edges)
            assert GraphProperties(Gcyc).girth() == N


# =============================================================================
# =============================================================================
