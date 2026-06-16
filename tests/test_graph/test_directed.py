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
    check_topological,
    depth_first_order,
    directed_cycle,
    topological_order,
)


@pytest.fixture
def tinyDG(data_dir):
    return Digraph.fromfile(data_dir / 'tinyDG.txt')


@pytest.fixture
def tinyDAG(data_dir):
    return Digraph.fromfile(data_dir / 'tinyDAG.txt')


@pytest.fixture
def loop_graph():
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


# Exercise 4.2.7
class TestIsMap:
    def test_loop_graph(self, loop_graph):
        G = loop_graph
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


# =============================================================================
# =============================================================================
