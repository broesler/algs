#!/usr/bin/env python3
# =============================================================================
#     File: bacon_numbers.py
#  Created: 2022-06-16 15:21
#   Author: Bernie Roesler
#
"""
Exercise 4.1.23 Print a histogram of Kevin Bacon numbers.
"""
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt
import pickle

from pathlib import Path

from algs.graph import BreadthFirstPaths

pkl_file = Path('./pkl/movies_SymbolGraph.pkl')
with open(pkl_file, 'rb') as fp:
    sg = pickle.load(fp)

q = 'Bacon, Kevin'
bfs = BreadthFirstPaths(sg.G, sg.index(q))

# Actors are even indices
actor_idx = sg.G.vertices()[::2]
dists = np.r_[[bfs.dist_to(v) for v in actor_idx]].astype(float)
dists = np.nan_to_num(dists, nan=-2)
dists /= 2  # only distance between actors
bins = np.arange(-1.5, np.max(dists) + 1.5)

nonames = list()
for i in np.argwhere(dists == -1).ravel():
    nonames.append(sg.name(i))
print(f"{len(nonames)} actors not connected!")

fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()
ax.hist(dists, bins=bins, density=True, rwidth=0.9, color='k')
ax.set(xlabel='x',
       ylabel='y')

plt.show()
# =============================================================================
# =============================================================================
