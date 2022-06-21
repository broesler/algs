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

import pickle
from pathlib import Path

from algs.graph import SymbolGraph, GraphProperties, CC_nr

FORCE_UPDATE = False

# datafile = Path('../data/movies.txt')
# datafile = Path('../data/movies-top-grossing.txt')
datafile = Path('../data/movies-hero.txt')

pkl_file = Path(f"./pkl/{datafile.stem}.pkl")
gp_file = Path(f"./pkl/{datafile.stem}_gp.pkl")

# -----------------------------------------------------------------------------
#         Load the data
# -----------------------------------------------------------------------------
if FORCE_UPDATE or not pkl_file.exists():
    sg = SymbolGraph.fromfile(datafile, delim='/', verbose=True)
    # sg = STGraph.fromadjfile(datafile, delim='/', verbose=True)
    with open(pkl_file, 'wb') as fp:
        pickle.dump(sg, fp)
else:
    with open(pkl_file, 'rb') as fp:
        sg = pickle.load(fp)

# -----------------------------------------------------------------------------
#         Process
# -----------------------------------------------------------------------------
G = sg.G

# Compute connected components
cc = CC_nr(G)

# Determine the largest component
M = cc.count()
components = cc.get_components()

sizes = [len(c) for c in components]
lt = [x for x in components if len(x) < 10]
max_c = max(range(M), key=lambda i: sizes[i])  # argmax

print(f"--- {datafile.name} ---")
print(f"{cc.count():,d} components.")
print(f"{len(lt):,d} components with < 10 vertices.")
print(f"{max(sizes):,d} vertices in the largest component ({max_c}).")

# Test if a name is in a component
q = 'Bacon, Kevin'
print(f"{q} is ", end='')
if sg.index(q) not in components[max_c]:
    print('not ', end='')
print('in the largest component.')

# -----------------------------------------------------------------------------
#         Find the properties of the largest component
# -----------------------------------------------------------------------------
# NOTE The ϵ(v) algorithm is O(V²) -> O(V³) for diameter/radius/center!!
i = max_c
# i = 2
comp = components[i]

if FORCE_UPDATE or not gp_file.exists():
    gp = GraphProperties(G, vertices=comp, verbose=True)
else:
    with open(gp_file, 'rb') as fp:
        gp = pickle.load(fp)

c = gp.center()
p = gp.periphery()
print(f"There are {len(c):,d} center vertices.")
print(f"There are {len(p):,d} periphery vertices.")

print(f"--- Properties of Component {i} ---")
print('eccentricity:', gp.eccentricity(comp[0]))
print('    diameter:', gp.diameter())
print('      radius:', gp.radius())
print('      center:', [sg.name(v) for v in c[:3]])
print('   periphery:', [sg.name(v) for v in p[:3]])
print('       girth:', gp.girth())

# Store expensive properties computations
if FORCE_UPDATE or not gp_file.exists():
    with open(gp_file, 'wb') as fp:
        pickle.dump(gp, fp)

# -----------------------------------------------------------------------------
#         Output
# -----------------------------------------------------------------------------

# --- movies-top-grossing.txt ---
# 2 components.
# 0 components with < 10 vertices.
# 8,440 vertices in the largest component (0).
# Bacon, Kevin is in the largest component.
# There are 1 center vertices.
# There are 2,950 periphery vertices.
# --- Properties of Component 0 ---
# eccentricity: 9
#     diameter: 12
#       radius: 6
#       center: ['Howard, Clint']
#    periphery: ['Akinnuoye-Agbaje, Adewale', 'Allen, Kayla', 'Callow, Simon']
#        girth: 4

# --- movies-hero.txt ---
# 112 components.
# 70 components with < 10 vertices.
# 1,405 vertices in the largest component (0).
# Bacon, Kevin is in the largest component.
# There are 1 center vertices.
# There are 67 periphery vertices.
# eccentricity: 13
#     diameter: 24
#       radius: 12
#       center: ['Clemenson, Christian']
#    periphery: ['Arne, Peter', 'Brunius, Jacques B.', 'Bryan, Dora']
#        girth: 4

# =============================================================================
# =============================================================================
