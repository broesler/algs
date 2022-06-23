#!/usr/bin/env python3
# =============================================================================
#     File: dfs_path_lengths.py
#  Created: 2022-06-22 21:30
#   Author: Bernie Roesler
#
"""
Exercise 4.1.47: Test probability of finding a path between two random vertices
and length of path when found.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

from algs.graph import DepthFirstPaths_nr
from algs.graph.random import (erdos_renyi, random_simple_graph,
                               random_grid_graph)

rng = np.random.default_rng(seed=565656)

# Inputs:
# * N graphs generated
# * V
# * E -> E/V gives sparsity. E in [V-1, V(V-1)/2] for connected graph, so
#        1 < E/V < V^0.5 is sparse, E/V ~ V is dense
# Each graph:
# * T random pairs of vertices attempted in a given graph

# Outputs:
# Each trial:
# * whether or not s and t are connected
# * path length if connected
# Each graph:
# * fraction of trials that resulted in a path
# * average path length
# Aggregate over N graphs:
# * fraction of trials that resulted in a path
# * average path length

generate_graph = random_simple_graph

N = 30   # graphs to generate
T = 10  # trials per graph

V = 100
# Es = np.r_[V // 2, V-1, int(V**1.5), V*(V-1) // 2]
Es = np.geomspace(V//2, V*(V-1)//2, num=20).astype(int)

data = np.full(len(Es)*N*T, np.nan)
index = pd.MultiIndex.from_product((Es, range(N), range(T)), 
                                   names=['E', 'N', 'T'])
df = pd.Series(data=data, index=index)

for E in tqdm(Es):
    for i in range(N):
        G = generate_graph(V, E)
        for j in range(T):
            s, t = rng.integers(V, size=2)
            dfs = DepthFirstPaths_nr(G, s)
            if dfs.has_path_to(t):
                df.loc[(E, i, j)] = len(dfs.path_to(t))

# Process: average over trials
tf = (df.reset_index()
        .rename({0: 'path length'}, axis=1)
        .assign(count=lambda x: ~np.isnan(x['path length']) / (N*T))
        .groupby('E')
        .agg({'path length': np.nanmean, 'count': np.sum})
        .assign(VoE=V/Es)
        .assign(EoV=Es/V)
        )

print(tf)

fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()
ax.scatter(tf['EoV'], tf['path length'])

ax.set_ylim((0, 1.1*50))
ax.set(xlabel='density (E/V)',
       ylabel='path length')

# Plot the count fraction on the other axis
ax1 = ax.twinx()
ax1.scatter(tf['EoV'], tf['count'], c='C3')
ax1.set_ylabel('fraction connected')
ax1.set_ylim((0, 1.1))
ax1.grid('off')

plt.show()

# =============================================================================
# =============================================================================
