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
import pickle
import numpy as np
from pathlib import Path

from algs.graph import STGraph, SymbolGraph, GraphProperties, CC, print_adj

FORCE_UPDATE = False
pkl_file = Path('./pkl/movies_SymbolGraph.pkl')
# pkl_file = Path('./pkl/movies_STGraph.pkl')

# ----------------------------------------------------------------------------- 
#         Load the data
# -----------------------------------------------------------------------------
if FORCE_UPDATE or not pkl_file.exists():
    sg = SymbolGraph.fromfile(Path('../data/movies.txt'), delim='/', verbose=True)
    # sg = STGraph.fromadjfile(Path('../data/movies.txt'), delim='/', verbose=True)
    with open(pkl_file, 'wb') as fp:
        pickle.dump(sg, fp)
else:
    with open(pkl_file, 'rb') as fp:
        sg = pickle.load(fp)

# ----------------------------------------------------------------------------- 
#         Process
# -----------------------------------------------------------------------------
G = sg.G

# Code for STGraph:
# def print_adj(G, s):
#     print(s)
#     for w in sg.adj(s):
#         print(' ', w)
# print_adj(sg, 'Top Gun (1986)')
# print_adj(sg, 'Cruise, Tom')

sys.setrecursionlimit(G.V+1)  # needed for DFS

# Compute connected components
cc = CC(G)

# lt = [x for x in cc.sizes if x < 10]

print(f"{cc.count():,d} components.")
# print(f"{len(lt):,d} components < 10.")
# print(f"{max(cc.sizes):,d} vertices in largest component.")


# Find the properties of the largest component subgraph
# v = cc.vertices(np.argmax(cc.sizes))

# TODO how to operate on a subgraph (list of vertices)??
# gp = GraphProperties(G)

# =============================================================================
# =============================================================================
