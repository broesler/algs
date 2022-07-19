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


def rotate(a, n):
    return a[n:] + a[:n]


N = 5  # word length

wordfile = Path(f"../data/words{N}.txt")
words = IndexSet()
with open(wordfile, 'r') as fp:
    for line in fp.readlines():
        words.add(line.strip())

# Build the graph
V = len(words)
G = Graph(V)

# Web Exercise 11: Slow O(N²) method:
# for v in words:
#     for w in words:
#         if len(v) != len(w):
#             raise ValueError('{v} and {w} must have same length!')
#         i, j = words.index(v), words.index(w)
#         if is_neighbor(v, w):
#             G.add_edge(i, j)

# Web Exercise 12: Faster method
# Sort the list N times, each time rotating the words by 1 character, such that
# words that differ by 1 character are consecutive in the list. Then, we only
# have to check N-1 pairs.
for n in range(N):
    sorted_words = sorted(words, key=lambda x: rotate(x, n))
    for i in range(V-1):
        # Check if last letters match
        if is_neighbor(sorted_words[i], sorted_words[i+1]):
            v = words.index(sorted_words[i])
            w = words.index(sorted_words[i+1])
            G.add_edge(v, w)


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
