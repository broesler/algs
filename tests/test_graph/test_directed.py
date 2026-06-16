#!/usr/bin/env python3
# =============================================================================
#     File: test_directed.py
#  Created: 2026-06-15 16:39
#   Author: Bernie Roesler
# =============================================================================

"""Tests for directed graph algorithms."""

import pytest

from algs.graph.directed import Digraph


@pytest.fixture
def tinyDG(data_dir):
    return Digraph.fromfile(data_dir / 'tinyDG.txt')


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
    def test_loop_graph(self):
        # Loop graph is a map
        V = 5
        G = Digraph(V)
        for i in range(V):
            G.add_edge(i, (i + 1) % V)
        assert G.is_map

    def test_line_graph(self):
        # Line graph is not a map
        V = 5
        G = Digraph(V)
        for i in range(V - 1):
            G.add_edge(i, i + 1)
        assert not G.is_map
        G.add_edge(V - 1, V - 1)  # add self-loop
        assert G.is_map

# =============================================================================
# =============================================================================
