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

from algs.graph import STGraph, SymbolGraph, GraphProperties, CC

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
sys.setrecursionlimit(G.V + 1)  # needed for DFS

def argmax(a):
    return max(range(len(a)), key=lambda i: a[i])

# Compute connected components
cc = CC(G)

# Determine the largest component
M = cc.count()
components = cc.get_components()

sizes = [len(c) for c in components]
lt = [x for x in components if len(x) < 10]
# max_c = max(range(M), key=lambda i: sizes[i])
max_c = argmax(sizes)

print('--- movies.txt ---')
print(f"{cc.count():,d} components.")
print(f"{len(lt):,d} components with < 10 vertices.")
print(f"{max(sizes):,d} vertices in the largest component ({max_c}).")

# Test if a name is in a component
q = 'Bacon, Kevin'
print(f"{q} is ", end='')
if sg.index(q) not in components[max_c]:
    print('not ', end='')
print('in the largest component.')

# Find the properties of the largest component -- SLOW!! Test on other.
# i = max_c # == 0
i = 2
comp = components[i]
gp = GraphProperties(G, vertices=comp, verbose=False)
print(f"--- Properties of Component {i} ---")
print('eccentricity:', gp.eccentricity(comp[0]))
print('    diameter:', gp.diameter())
print('      radius:', gp.radius())
print('      center:', sg.name(gp.center()))
print('       girth:', gp.girth())

# =============================================================================
# =============================================================================
