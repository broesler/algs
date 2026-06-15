#!/usr/bin/env python3
# =============================================================================
#     File: test_search.py
#  Created: 2026-06-15 15:03
#   Author: Bernie Roesler
# =============================================================================

"""Tests for graph search algorithms."""

import pytest

from algs.graph.search import (
    BreadthFirstSearch,
    DepthFirstSearch,
    DepthFirstSearch_nr,
    DepthFirstSearch_nr_simple,
    UFSearch,
    find_cycle_path,
    find_min_cycle,
    has_cycle,
)
from algs.graph.undirected import Graph, SimpleGraph

# Expected values for tinyCG
EXPECT_DFS = {
    0: [0],
    1: [0, 2, 1],
    2: [0, 2],
    3: [0, 2, 3],
    4: [0, 2, 3, 4],
    5: [0, 2, 3, 5],
}

EXPECT_DFS_S = {
    0: [0],
    1: [0, 5, 3, 2, 1],
    2: [0, 5, 3, 2],
    3: [0, 5, 3],
    4: [0, 5, 3, 2, 4],
    5: [0, 5],
}

EXPECT_BFS = {
    0: [0],
    1: [0, 1],
    2: [0, 2],
    3: [0, 2, 3],
    4: [0, 2, 4],
    5: [0, 5],
}


@pytest.fixture
def acyclicG(GraphType):
    V = 5
    G = GraphType(V)
    for i in range(V - 1):
        G.add_edge(i, i + 1)
    return G


@pytest.mark.parametrize('GraphType', [Graph, SimpleGraph])
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


@pytest.mark.parametrize('GraphType', [Graph, SimpleGraph])
@pytest.mark.parametrize('recursive', [True, False])
def test_has_cycle(tinyG, acyclicG, recursive):
    assert has_cycle(tinyG, 0, recursive=recursive)
    assert not has_cycle(acyclicG, 0, recursive=recursive)


@pytest.mark.parametrize('GraphType', [Graph, SimpleGraph])
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
        'DFS, EXPECT',
        [
            (DepthFirstSearch, EXPECT_DFS),
            (DepthFirstSearch_nr, EXPECT_DFS),
            (DepthFirstSearch_nr_simple, EXPECT_DFS_S),
        ],
    )
    def test_dfs_path_to(self, tinyCG, DFS, EXPECT):
        dfs = DFS(tinyCG, 0)
        for v in tinyCG.vertices():
            assert list(dfs.path_to(v)) == EXPECT[v]

    def test_bfs_path_to(self, tinyCG):
        bfs = BreadthFirstSearch(tinyCG, 0)
        for v in tinyCG.vertices():
            assert list(bfs.path_to(v)) == EXPECT_BFS[v]
        assert [bfs.dist_to(v) for v in tinyCG.vertices()] == [0, 1, 1, 2, 2, 1]

    @pytest.mark.parametrize('GraphSearch', [DepthFirstSearch, DepthFirstSearch_nr])
    def test_leaf_CG(self, GraphSearch, tinyCG):
        assert GraphSearch(tinyCG, 0).leaf == 1

    @pytest.mark.parametrize('GraphSearch', [DepthFirstSearch, DepthFirstSearch_nr])
    def test_leaf_G(self, GraphSearch, tinyG):
        assert GraphSearch(tinyG, 0).leaf == 3
        assert GraphSearch(tinyG, 6).leaf == 2
        assert GraphSearch(tinyG, 7).leaf == 8


@pytest.mark.parametrize('GraphType', [Graph, SimpleGraph])
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
