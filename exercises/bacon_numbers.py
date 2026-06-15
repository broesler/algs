#!/usr/bin/env python3
# =============================================================================
#     File: bacon_numbers.py
#  Created: 2022-06-16 15:21
#   Author: Bernie Roesler
# =============================================================================

"""Exercise 4.1.23: Print a histogram of Kevin Bacon numbers."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from algs.graph import BreadthFirstSearch, SymbolGraph

data_file = Path(__file__).parent.parent / 'data' / 'movies.txt'
sg = SymbolGraph.fromfile(data_file, delim='/')

q = 'Bacon, Kevin'
bfs = BreadthFirstSearch(sg.graph, sg.index_of(q))

# Actors are even indices
actor_idx = sg.graph.vertices()[::2]
dists = np.r_[[bfs.dist_to(v) for v in actor_idx]].astype(float)
dists = np.nan_to_num(dists, nan=-2)
dists /= 2  # only distance between actors
bins = np.arange(-1.5, np.max(dists) + 1.5)

nonames = []
for i in np.argwhere(dists == -1).ravel():
    nonames.append(sg.name_of(i))
print(f"{len(nonames)} actors not connected!")

fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()
ax.hist(dists, bins=bins, density=True, rwidth=0.9, color='tab:blue', alpha=0.8)
ax.set(xlabel='x', ylabel='y')

plt.show()
# =============================================================================
# =============================================================================
