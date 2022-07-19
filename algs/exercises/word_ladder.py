#!/usr/bin/env python3
# =============================================================================
#     File: word_ladder.py
#  Created: 2022-07-18 21:21
#   Author: Bernie Roesler
#
"""
Find the word ladder between two inputs.
"""
# =============================================================================

from pathlib import Path

from algs.search import IndexSet
from algs.graph import Graph, BreadthFirstPaths


def is_neighbor(a, b):
    """Return True if `a` and `b` differ by exactly one letter."""
    assert len(a) == len(b)
    diffs = 0
    for i in range(len(a)):
        if a[i] != b[i]:
            diffs += 1
        if diffs > 1:
            return False
    return True


N = 5  # word length

wordfile = Path(f"../data/words{N}.txt")
words = IndexSet()
with open(wordfile, 'r') as fp:
    for line in fp.readlines():
        words.add(line.strip())

# Build the graph
V = len(words)
G = Graph(V)
for v in words:
    for w in words:
        if len(v) != len(w):
            raise ValueError('{v} and {w} must have same length!')
        i, j = words.index(v), words.index(w)
        if is_neighbor(v, w):
            G.add_edge(i, j)


if __name__ == "__main__":
    a = 'white'
    b = 'house'
    bfs = BreadthFirstPaths(G, words.index(a))
    if not bfs.has_path_to(words.index(b)):
        print('not connected.')
    else:
        for v in bfs.path_to(words.index(b)):
            print(words.key(v))


# =============================================================================
# =============================================================================
