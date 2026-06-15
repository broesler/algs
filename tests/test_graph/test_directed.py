#!/usr/bin/env python3
# =============================================================================
#     File: test_directed.py
#  Created: 2026-06-15 16:39
#   Author: Bernie Roesler
# =============================================================================

"""Tests for directed graph algorithms."""

from pathlib import Path

import pytest

from algs.graph.directed import Digraph

DATA_DIR = Path(__file__).resolve().parents[2] / 'data'


@pytest.fixture
def tinyDG():
    return Digraph.fromfile(DATA_DIR / 'tinyDG.txt')


class TestTinyDG:
    # tinyDG.txt contains the following edges:
    EXPECT_EDGES = [
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
    ]

    def test_constructor(self):
        V = 13
        G = Digraph(V)
        assert list(G.vertices()) == list(range(G.V))
        for v, w in self.EXPECT_EDGES:
            G.add_edge(v, w)
            assert G.has_edge(v, w)
        assert not G.has_edge(0, 6)
        assert G.E == 22

    def test_fromfile(self, tinyDG):
        assert tinyDG.V == 13
        assert tinyDG.E == 22
        for v, w in self.EXPECT_EDGES:
            assert tinyDG.has_edge(v, w)
        assert not tinyDG.has_edge(0, 6)
        assert list(tinyDG.vertices()) == list(range(tinyDG.V))

    def test_adj(self, tinyDG):
        EXPECT_ADJ = {
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
            assert list(tinyDG.adj(v)) == EXPECT_ADJ[v]

    def test_degrees(self, tinyDG):
        EXPECT_INDEGREES = (2, 1, 2, 2, 3, 2, 1, 1, 1, 3, 1, 1, 2)
        EXPECT_OUTDEGREES = (2, 0, 2, 2, 2, 1, 3, 2, 2, 2, 1, 2, 1)
        for v in tinyDG.vertices():
            assert tinyDG.indegree(v) == EXPECT_INDEGREES[v]
            assert tinyDG.outdegree(v) == EXPECT_OUTDEGREES[v]

    def test_copy(self, tinyDG):
        H = tinyDG.copy()
        for v in tinyDG.vertices():
            assert H.adj(v) == tinyDG.adj(v)
            assert H._adj[v] is not tinyDG._adj[v]

    def test_sources(self, tinyDG):
        EXPECT_SOURCES = []
        assert tinyDG.sources == EXPECT_SOURCES

    def test_sinks(self, tinyDG):
        EXPECT_SINKS = [1]
        assert tinyDG.sinks == EXPECT_SINKS


# =============================================================================
# =============================================================================
