#!/usr/bin/env python3
# =============================================================================
#     File: test_directed.py
#  Created: 2026-06-15 16:39
#   Author: Bernie Roesler
# =============================================================================

"""Tests for directed graph algorithms."""

import pytest

from algs.graph.directed import (
    Digraph,
    KosarajuSCC,
    TransitiveClosure,
    check_topological,
    depth_first_order,
    directed_cycle,
    eulerian_cycle,
    hamiltonian_path,
    topological_order,
)
from algs.graph.search import (
    BreadthFirstSearch,
    DepthFirstSearch,
    DepthFirstSearch_nr,
    DepthFirstSearch_nr_simple,
)
from algs.graph.undirected import UFSearch


@pytest.fixture
def tinyDG(data_dir):
    return Digraph.fromfile(data_dir / 'tinyDG.txt')


@pytest.fixture
def tinyDAG(data_dir):
    return Digraph.fromfile(data_dir / 'tinyDAG.txt')


@pytest.fixture
def cycle_graph():
    V = 5
    G = Digraph(V)
    for i in range(V):
        G.add_edge(i, (i + 1) % V)
    return G


@pytest.fixture
def line_graph():
    V = 5
    G = Digraph(V)
    for i in range(V - 1):
        G.add_edge(i, i + 1)
    return G


class TestNonSimple:
    @pytest.fixture
    @staticmethod
    def make_tinyDG(data_dir):
        def _make_tinyDG(**kwargs):
            return Digraph.fromfile(data_dir / 'tinyDG.txt', **kwargs)

        return _make_tinyDG

    def test_no_self_loops(self, make_tinyDG):
        G = make_tinyDG(self_loops=False)
        assert not G.has_self_loop
        with pytest.raises(ValueError):
            G.add_edge(0, 0)

    def test_self_loops(self, make_tinyDG):
        G = make_tinyDG(self_loops=True)
        assert not G.has_self_loop
        assert G.num_self_loops == 0
        G.add_edge(1, 1)
        assert G.has_self_loop
        assert G.num_self_loops == 1
        G.add_edge(1, 1)
        G.add_edge(1, 1)
        G.add_edge(9, 9)
        assert G.num_self_loops == 4

    def test_no_parallel_edges(self, make_tinyDG):
        G = make_tinyDG(parallel=False)
        assert not G.has_parallel_edges
        assert G.num_parallel_edges == 0
        G.add_edge(0, 1)
        assert not G.has_parallel_edges
        assert G.num_parallel_edges == 0

    def test_parallel_edges(self, make_tinyDG):
        G = make_tinyDG(parallel=True)
        assert not G.has_parallel_edges
        G.add_edge(0, 1)
        assert G.has_parallel_edges
        assert G.num_parallel_edges == 1
        G.add_edge(2, 3)
        assert G.has_parallel_edges
        assert G.num_parallel_edges == 2


class TestTinyDG:
    # tinyDG.txt contains the following edges:
    @pytest.fixture(scope='class')
    @staticmethod
    def expect_edges():
        return (
            (7, 6),
            (6, 9),
            (6, 4),
            (0, 5),
            (5, 4),
            (8, 7),
            (7, 8),
            (3, 5),
            (4, 3),
            (11, 4),
            (10, 12),
            (8, 9),
            (9, 11),
            (9, 10),
            (12, 9),
            (11, 12),
            (2, 0),
            (0, 1),
            (6, 0),
            (3, 2),
            (2, 3),
            (4, 2),
        )

    def test_constructor(self, expect_edges):
        V = 13
        G = Digraph(V)
        assert list(G.vertices()) == list(range(G.V))
        for v, w in expect_edges:
            G.add_edge(v, w)
            assert G.has_edge(v, w)
        assert not G.has_edge(0, 6)
        assert G.V == 13
        assert G.E == 22

    def test_fromfile(self, tinyDG, expect_edges):
        assert tinyDG.V == 13
        assert tinyDG.E == 22
        for v, w in expect_edges:
            assert tinyDG.has_edge(v, w)
        assert not tinyDG.has_edge(0, 6)
        assert list(tinyDG.vertices()) == list(range(tinyDG.V))

    def test_adj(self, tinyDG):
        expect_adj = {
            0: [5, 1],
            1: [],
            2: [0, 3],
            3: [5, 2],
            4: [3, 2],
            5: [4],
            6: [9, 4, 0],
            7: [6, 8],
            8: [7, 9],
            9: [11, 10],
            10: [12],
            11: [4, 12],
            12: [9],
        }

        for v in tinyDG.vertices():
            assert list(tinyDG.adj(v)) == expect_adj[v]

    def test_degrees(self, tinyDG):
        expect_indegrees = (2, 1, 2, 2, 3, 2, 1, 1, 1, 3, 1, 1, 2)
        expect_outdegrees = (2, 0, 2, 2, 2, 1, 3, 2, 2, 2, 1, 2, 1)
        for v in tinyDG.vertices():
            assert tinyDG.indegree(v) == expect_indegrees[v]
            assert tinyDG.outdegree(v) == expect_outdegrees[v]

    def test_copy(self, tinyDG):
        H = tinyDG.copy()
        for v in tinyDG.vertices():
            assert H.adj(v) == tinyDG.adj(v)
            assert H._adj[v] is not tinyDG._adj[v]

    def test_sources(self, tinyDG):
        expect_sources = []
        assert tinyDG.sources == expect_sources

    def test_sinks(self, tinyDG):
        expect_sinks = [1]
        assert tinyDG.sinks == expect_sinks

    def test_is_map(self, tinyDG):
        assert not tinyDG.is_map

    def test_reverse(self, tinyDG):
        H = tinyDG.reverse()
        for v in tinyDG.vertices():
            for w in tinyDG.adj(v):
                assert v in H.adj(w)


# TODO test SymbolDigraph

# Exercise 4.2.7
class TestIsMap:
    def test_cycle_graph(self, cycle_graph):
        G = cycle_graph
        assert G.is_map

    def test_line_graph(self, line_graph):
        G = line_graph
        V = G.V
        assert not G.is_map
        G.add_edge(V - 1, V - 1)  # add self-loop
        assert G.is_map


class TestDirectedCycle:
    def test_cycle(self, tinyDG):
        cycle = directed_cycle(tinyDG)
        assert cycle == [3, 5, 4, 3]
        for i in range(len(cycle) - 1):
            assert tinyDG.has_edge(cycle[i], cycle[i + 1])

    def test_acyclic(self, tinyDAG):
        assert not directed_cycle(tinyDAG)


class TestStronglyConnectedComponents:
    def test_tinyDG(self, tinyDG):
        scc = KosarajuSCC(tinyDG)
        assert scc.count == 5
        expect_components = [[0, 2, 3, 4, 5], [1], [6], [7, 8], [9, 10, 11, 12]]
        assert scc.get_components(sort=True) == expect_components

    def test_tinyDAG(self, tinyDAG):
        scc = KosarajuSCC(tinyDAG)
        V = tinyDAG.V
        # each vertex is its own component
        assert scc.count == V
        expect_components = [[x] for x in range(V)]
        # No guarantee on order of components, so sort them first
        assert scc.get_components(sort=True) == expect_components


def test_depth_first_order(tinyDG):
    expect_pre = [0, 5, 4, 3, 2, 1, 6, 9, 11, 12, 10, 7, 8]
    expect_post = [2, 3, 4, 5, 1, 0, 12, 11, 10, 9, 6, 8, 7]
    expect_reverse_post = [7, 8, 6, 9, 10, 11, 12, 0, 1, 5, 4, 3, 2]
    assert list(reversed(expect_post)) == expect_reverse_post
    orders = depth_first_order(tinyDG)
    assert orders.pre == expect_pre
    assert orders.post == expect_post
    assert orders.reverse_post == expect_reverse_post


class TestTopologicalOrder:
    def test_cyclic(self, tinyDG):
        assert directed_cycle(tinyDG)
        t = topological_order(tinyDG)
        assert not t

    def test_acyclic(self, tinyDAG):
        assert not directed_cycle(tinyDAG)
        t = topological_order(tinyDAG)
        expect_t = [8, 7, 2, 3, 0, 6, 9, 10, 11, 12, 1, 5, 4]
        assert t == expect_t
        p = depth_first_order(tinyDAG)
        assert t == p.reverse_post

    def test_check_topological(self, tinyDAG):
        t = topological_order(tinyDAG)
        assert check_topological(tinyDAG, t)
        t[0], t[1] = t[1], t[0]  # swap two vertices
        assert not check_topological(tinyDAG, t)


class TestTransitiveClosure:
    def test_cycle_graph(self, cycle_graph):
        G = cycle_graph
        tc = TransitiveClosure(G)
        for v in G.vertices():
            for w in G.vertices():
                assert tc.reachable(v, w)

    def test_line_graph(self, line_graph):
        G = line_graph
        tc = TransitiveClosure(G)
        for v in G.vertices():
            for w in G.vertices():
                if v <= w:
                    assert tc.reachable(v, w)
                else:
                    assert not tc.reachable(v, w)


class TestEulerianCycle:
    def test_cycle(self, cycle_graph):
        G = cycle_graph
        cycle = eulerian_cycle(G)
        assert cycle == [4, 0, 1, 2, 3, 4]
        for i in range(len(cycle) - 1):
            assert G.has_edge(cycle[i], cycle[i + 1])

    def test_no_cycle(self, line_graph):
        G = line_graph
        assert not eulerian_cycle(G)


class TestHamiltonianPath:
    def test_has_path(self, line_graph):
        G = line_graph
        h = hamiltonian_path(G)
        assert h is not None
        assert h == list(range(G.V))
        for i in range(len(h) - 1):
            assert G.has_edge(h[i], h[i + 1])

    def test_no_path(self, tinyDAG):
        assert not hamiltonian_path(tinyDAG)

    @pytest.mark.parametrize('graph_name', ['cycle_graph', 'tinyDG'])
    def test_not_dag(self, graph_name, request):
        G = request.getfixturevalue(graph_name)
        with pytest.raises(ValueError, match="not a DAG"):
            assert not hamiltonian_path(G)


# -----------------------------------------------------------------------------
#         Test Search
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    'search_class',
    [
        DepthFirstSearch,
        DepthFirstSearch_nr,
        DepthFirstSearch_nr_simple,
        BreadthFirstSearch,
    ],
)
class TestSearch:
    def test_single_source(self, tinyDG, search_class):
        # vertices > 6 not reachable from 0
        dfs = search_class(tinyDG, 0)
        assert dfs.sources == [0]
        assert dfs.count == 6
        assert all(dfs.has_path_to(v) for v in range(6))
        assert all(not dfs.has_path_to(v) for v in range(6, tinyDG.V))
        # vertex 7 connected to everything
        dfs = search_class(tinyDG, 7)
        assert dfs.sources == [7]
        assert dfs.count == tinyDG.V
        assert all(dfs.has_path_to(v) for v in tinyDG.vertices())
        # vertex 9 connected to everything except 6, 7, 8
        dfs = search_class(tinyDG, 9)
        assert dfs.sources == [9]
        assert dfs.count == 10
        not_connected = {6, 7, 8}
        assert all(dfs.has_path_to(v) for v in set(tinyDG.vertices()) - not_connected)
        assert all(not dfs.has_path_to(v) for v in not_connected)

    def test_multiple_sources(self, tinyDG, search_class):
        # vertices 6, 9 connected to everything except 7, 8
        dfs = search_class(tinyDG, [6, 9])
        assert dfs.sources == [6, 9]
        assert dfs.count == 11
        assert all(dfs.has_path_to(v) for v in set(tinyDG.vertices()) - {7, 8})


def test_ufsearch(tinyDG):
    with pytest.raises(ValueError, match="undirected graph"):
        UFSearch(tinyDG, 0)


# ----- DFS Paths -----
# TODO test multiple sources: DepthFirstSearch(tinyDG, [0, 6])
# Paths starting at 0 -> k
EXPECT_DFS_0 = {
    0: [0],
    1: [0, 1],
    2: [0, 5, 4, 3, 2],
    3: [0, 5, 4, 3],
    4: [0, 5, 4],
    5: [0, 5],
    6: None,
    7: None,
    8: None,
    9: None,
    10: None,
    11: None,
    12: None,
}


class TestPaths:
    @pytest.mark.parametrize(
        'search_class, expected_paths',
        [
            (DepthFirstSearch, EXPECT_DFS_0),
            (DepthFirstSearch_nr, EXPECT_DFS_0),
            # (DepthFirstSearch_nr_simple, EXPECT_DFS_S_0),  # TODO
        ],
    )
    def test_dfs_path_to(self, tinyDG, search_class, expected_paths):
        dfs = search_class(tinyDG, 0)
        actual_paths = {
            v: list(dfs.path_to(v)) if dfs.has_path_to(v) else None
            for v in tinyDG.vertices()
        }
        assert actual_paths == expected_paths

    def test_bfs_path_to(self, tinyDG):
        # TODO test multiple sources: BreadthFirstSearch(tinyDG, [0, 6])
        expect_paths = {
            0: [0],
            1: [0, 1],
            2: [0, 5, 4, 2],
            3: [0, 5, 4, 3],
            4: [0, 5, 4],
            5: [0, 5],
            6: None,
            7: None,
            8: None,
            9: None,
            10: None,
            11: None,
            12: None,
        }
        bfs = BreadthFirstSearch(tinyDG, 0)
        actual_paths = {
            v: list(bfs.path_to(v)) if bfs.has_path_to(v) else None
            for v in tinyDG.vertices()
        }
        assert actual_paths == expect_paths

    def test_bfs_dist_to(self, tinyDG):
        # TODO test multiple sources: BreadthFirstSearch(tinyDG, [0, 6])
        bfs = BreadthFirstSearch(tinyDG, 0)
        expect_dist_to = [0, 1, 3, 3, 2, 1] + 7 * [None]
        actual_dist_to = [bfs.dist_to(v) for v in tinyDG.vertices()]
        assert actual_dist_to == expect_dist_to


@pytest.mark.parametrize('search_class', [DepthFirstSearch, DepthFirstSearch_nr])
class TestLeaf:
    def test_leaf_DG(self, search_class, tinyDG):
        assert search_class(tinyDG, 0).leaf == 2
        assert search_class(tinyDG, 1).leaf == 1  # dead-end!

    def test_leaf_DAG(self, search_class, tinyDAG):
        assert search_class(tinyDAG, 0).leaf == 4
        assert search_class(tinyDAG, 1).leaf == 1  # dead-end!
        assert search_class(tinyDAG, 6).leaf == 12
        assert search_class(tinyDAG, 7).leaf == 12


# =============================================================================
# =============================================================================
