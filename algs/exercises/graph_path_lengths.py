#!/usr/bin/env python3
# =============================================================================
#     File: graph_path_lengths.py
#  Created: 2022-06-22 21:30
#   Author: Bernie Roesler
#
"""
Exercise 4.1.47: Test probability of finding a path between two random vertices
and length of path when found.

Inputs:
* N graphs generated
* V
* E -> E/V gives sparsity. E in [V-1, V(V-1)/2] for connected graph, so
       1 < E/V < V^0.5 is sparse, E/V ~ V is dense
Each graph:
* T random pairs of vertices attempted in a given graph

Outputs:
Each trial:
* whether or not s and t are connected
* path length if connected
Each graph:
* fraction of trials that resulted in a path
* average path length
Aggregate over N graphs:
* fraction of trials that resulted in a path
* average path length
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from tqdm import tqdm

from algs.graph import DepthFirstPaths_nr, BreadthFirstPaths, CC_nr, Bipartite
from algs.graph.random import erdos_renyi, random_simple_graph

rng = np.random.default_rng(seed=565656)

FORCE_UPDATE = True
SAVE_FIGS = False

generate_graph = random_simple_graph
tag = 'simple'

# generate_graph = erdos_renyi
# tag = 'erdos'

V = 100

pkl_file = Path(f"./pkl/graph_path_lengths_{tag}_V{V}.pkl")

if FORCE_UPDATE or not pkl_file.exists():
    N = 30   # graphs to generate
    T = 10  # trials per graph
    Es = np.geomspace(V**0.5, V*(V-1)//2, num=20).astype(int)

    index = pd.MultiIndex.from_product((Es, range(N), range(T)),
                                       names=['E', 'N', 'T'])
    data = np.full((len(Es)*N*T, 3), np.nan)
    df = pd.DataFrame(index=index, columns=['depth', 'breadth', 'comps'], data=data)
    cf = pd.Series(index=index.droplevel(-1).drop_duplicates(), 
                   data=np.full(len(Es)*N, np.nan))
    bf = pd.Series(index=index.droplevel(-1).drop_duplicates(), 
                   data=np.full(len(Es)*N, np.nan))

    for E in tqdm(Es):
        for i in range(N):
            G = generate_graph(V, E)
            cc = CC_nr(G)
            bp = Bipartite(G)
            cf.loc[(E, i)] = cc.count()
            bf.loc[(E, i)] = bp._count
            for j in range(T):
                s, t = rng.integers(V, size=2)
                dfs = DepthFirstPaths_nr(G, s)
                bfs = BreadthFirstPaths(G, s)
                if dfs.has_path_to(t):
                    df.loc[(E, i, j), 'depth'] = len(dfs.path_to(t))
                if bfs.has_path_to(t):
                    df.loc[(E, i, j), 'breadth'] = len(bfs.path_to(t))

    # Average components over trials
    cf = cf.groupby('E').mean()
    bf = bf.groupby('E').mean()

    # Average path lengths over trials
    tf = (df.reset_index()
            .assign(count=lambda x: ~np.isnan(x['depth']) / (N*T))
            .groupby('E')
            .agg({'depth': np.nanmean, 'breadth': np.nanmean, 'count': np.sum})
            .assign(VoE=V/Es)
            .assign(EoV=Es/V)
            .assign(components=cf)
            .assign(bipartite_depth=bf)
          )

    with open(pkl_file, 'wb') as fp:
        pickle.dump((tf, cf, bf), fp)
else:
    with open(pkl_file, 'rb') as fp:
        tf, cf, bf = pickle.load(fp)


# -----------------------------------------------------------------------------
#         Plot
# -----------------------------------------------------------------------------
print(tf)

fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()
ax.scatter(tf['EoV'], tf['depth'], c='C0', zorder=3, label='DFS')
ax.scatter(tf['EoV'], tf['breadth'], c='C3', zorder=3, label='BFS')
ax.scatter(tf['EoV'], cf.values, c='C2', zorder=3, label='CC')
ax.scatter(tf['EoV'], bf.values, c='C4', zorder=3, label='BP')
# ax.axvline(1/2 * np.log(V), c='k', ls='--', alpha=0.5)
ax.axhline(V/2, c='k', ls='--', alpha=0.5)

ax.set(xlabel='density (E/V)', xscale='log',
       ylabel='path length, # components')
ax.set_xticks([V**-0.5, 1, V**0.5, (V-1)/2])
ax.set_xticklabels([r'$\frac{\sqrt{V}}{V}$',
                    '1',
                    r'$\sqrt{V}$',
                    r'$\frac{V-1}{2}$'])
ax.set_yticks(V*np.arange(0, 1.2, 0.2))
ax.set_yticklabels(['0'] + [f"{x:.1f}V" for x in np.arange(0.2, 1, 0.2)] + ['V'])
# ax.set_yticks([0, V//4, V//2, 3*V//4, V])
# ax.set_yticklabels(['0', r'$\frac{V}{4}$', r'$\frac{V}{2}$', r'$\frac{3V}{4}$', r'$V$'])
ax.legend()
ax.set_ylim(top=1.03*V)
ax.grid(which='both')

# Plot the count fraction on the other axis
ax1 = ax.twinx()
ax1.plot(tf['EoV'], tf['count'], c='k', alpha=0.5)
ax1.set_ylabel('fraction connected')
# Match tick marks
ax1.set_ylim(top=1.03)
ax1.grid(visible=False)

if SAVE_FIGS:
    fig.savefig(f"./figures/graph_path_lengths_{tag}_V{V}.png")

plt.show()

# =============================================================================
# =============================================================================
