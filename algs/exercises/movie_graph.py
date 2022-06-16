#!/usr/bin/env python3
# =============================================================================
#     File: movie_graph.py
#  Created: 2022-06-16 00:04
#   Author: Bernie Roesler
#
"""
Exercise 4.1.24 Connected components in the movies.txt graph.
"""
# =============================================================================

import sys
import numpy as np
from pathlib import Path

from algs.graph import SymbolGraph, GraphProperties, CC

# TODO save sg to pickle file.
sg = SymbolGraph.fromfile(Path('../data/movies.txt'), delim='/', verbose=True)
G = sg.G

sys.setrecursionlimit(G.V+1)  # needed for DFS

# Compute connected components
cc = CC(G)
lt = [x for x in cc.sizes if x < 10]

print(f"# components: {cc.count():,d}")
print(f"# components < 10: {len(lt):,d}")
print(f"Largest component: {max(cc.sizes):,d} vertices")

# Find the properties of the largest component subgraph
v = cc.vertices(np.argmax(cc.sizes))
# G.vertices = lambda: v
# G.V = len(v)

# TODO how to operate on a subgraph (list of vertices)??
gp = GraphProperties(G)

# =============================================================================
# =============================================================================
