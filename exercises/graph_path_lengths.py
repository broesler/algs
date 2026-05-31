#!/usr/bin/env python3
# =============================================================================
#     File: graph_path_lengths.py
#  Created: 2022-06-22 21:30
#   Author: Bernie Roesler
# =============================================================================

"""Exercise 4.1.47: Find a path between two random vertices.

Test probability of finding a path between two random vertices and length of
path when found.

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

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from algs.graph import Bipartite, BreadthFirstPaths, CC_nr, DepthFirstPaths_nr
from algs.graph.random import erdos_renyi, random_simple_graph  # noqa: F401

FORCE_UPDATE = False
SAVE_FIGS = False

V = 100  # number of vertices in each graph

PKL_PATH = Path(__file__).parent / 'pkl'
pkl_file = PKL_PATH / f"graph_path_lengths_V{V}.parquet"


def simulate_graphs(V, Es, N, T, generate_graph=None):
    """Yield a list of dicts of trial results, for use in a DataFrame.

    Parameters
    ----------
    V : int
        Number of vertices in each graph.
    Es : array-like
        List of edge counts to generate graphs with.
    N : int
        Number of graphs to generate for each edge count.
    T : int
        Number of trials to run for each graph.

    Yields
    ------
    result : dict
        Dictionary containing results for each trial, with keys:
        - 'E': Number of edges in the graph.
        - 'components': Number of connected components in the graph.
        - 'bipartite_depth': Count related to bipartite property of the graph.
        - 'depth': Length of path found by DFS (or NaN if no path).
        - 'breadth': Length of path found by BFS (or NaN if no path).
    """
    if generate_graph is None:
        generate_graph = random_simple_graph

    rng = np.random.default_rng(seed=565656)

    for E in tqdm(Es):
        for _ in range(N):
            G = generate_graph(V, E)
            cc_count = CC_nr(G).count()
            bp_count = Bipartite(G)._count

            for _ in range(T):
                s, t = rng.integers(V, size=2)
                dfs = DepthFirstPaths_nr(G, s)
                bfs = BreadthFirstPaths(G, s)

                yield {
                    'E': E,
                    'components': cc_count,
                    'bipartite_depth': bp_count,
                    'depth': len(dfs.path_to(t)) if dfs.has_path_to(t) else np.nan,
                    'breadth': len(bfs.path_to(t)) if bfs.has_path_to(t) else np.nan,
                }


if FORCE_UPDATE or not pkl_file.exists():
    N = 30  # graphs to generate
    T = 10  # trials per graph
    Es = np.geomspace(V**0.5, V * (V - 1) // 2, num=20).astype(int)

    # Build the DataFrame
    dfs = {
        graph_func.__name__: (
            pd.DataFrame(simulate_graphs(V, Es, N, T, generate_graph=graph_func))
            .groupby('E')
            # Average path lengths over trials
            .agg(
                depth=('depth', 'mean'),
                breadth=('breadth', 'mean'),
                components=('components', 'mean'),
                bipartite_depth=('bipartite_depth', 'mean'),
                valid_paths=('depth', 'count'),
            )
            .assign(
                count=lambda df_: df_['valid_paths'] / (N * T),
                EoV=lambda df_: df_.index / V,  # E is index
            )
            .drop(columns='valid_paths')
        )
        for graph_func in [random_simple_graph, erdos_renyi]
    }

    # Change names for plotting
    name_map = {'random_simple_graph': 'Simple', 'erdos_renyi': 'Erdős-Rényi'}
    graph_cat = pd.CategoricalDtype(name_map.values(), ordered=True)

    df = (
        pd.concat(dfs, names=['graph_type'])
        .reset_index(level='graph_type')
        .assign(
            graph_type=lambda df_: df_['graph_type'].map(name_map).astype(graph_cat)
        )
    )

    df.to_parquet(pkl_file)
else:
    df = pd.read_parquet(pkl_file)


# -----------------------------------------------------------------------------
#         Plot
# -----------------------------------------------------------------------------
print(df)

rename_map = {
    'depth': 'DFS',
    'breadth': 'BFS',
    'components': 'CC',
    'bipartite_depth': 'BP',
}

color_map = {
    'DFS': 'tab:blue',
    'BFS': 'tab:red',
    'CC': 'tab:green',
    'BP': 'tab:purple',
}

df_tidy = df.rename(columns=rename_map).melt(
    id_vars=['graph_type', 'EoV'],
    value_vars=list(rename_map.values()),
    var_name='metric',
    value_name='value',
)

fig, ax = plt.subplots(num=1, clear=True)
fig.set_size_inches((8, 6), forward=True)
ax_twin = ax.twinx()

sns.scatterplot(
    data=df_tidy,
    x='EoV',
    y='value',
    hue='metric',
    style='graph_type',
    palette=color_map,
    ax=ax,
)

# ax_twin.plot(df['EoV'], df['count'], color='k', alpha=0.5)
sns.lineplot(
    data=df,
    x='EoV',
    y='count',
    color='k',
    style='graph_type',
    alpha=0.5,
    ax=ax_twin,
)

# ax.axvline(1/2 * np.log(V), c='k', ls='--', alpha=0.5)
ax.axhline(V / 2, c='k', ls='--', alpha=0.5)

# Combine the legends
handles, labels = ax.get_legend_handles_labels()
handles_twin, labels_twin = ax_twin.get_legend_handles_labels()
ax.legend(handles + handles_twin, labels + labels_twin)
ax_twin.get_legend().remove()

ax.set(
    xlabel='density (E/V)',
    xscale='log',
    ylabel='path length, # components',
    ylim=(0, 1.03 * V),
)
ax_twin.set(
    ylabel='fraction connected',
    ylim=(0, 1.03),
)

ax.set_xticks([V**-0.5, 1, V**0.5, (V - 1) / 2])
ax.set_xticklabels([r'$\frac{\sqrt{V}}{V}$', '1', r'$\sqrt{V}$', r'$\frac{V-1}{2}$'])

y_ticks = np.arange(0, 1.2, 0.2)
ax.set_yticks(V * y_ticks)
ax.set_yticklabels(['0'] + [f"{x:.1f}V" for x in y_ticks[1:-1]] + ['V'])

# ax.set_yticks([0, V//4, V//2, 3*V//4, V])
# ax.set_yticklabels(
#     ['0', r'$\frac{V}{4}$', r'$\frac{V}{2}$', r'$\frac{3V}{4}$', r'$V$']
# )

ax.grid(which='both')
ax_twin.grid(visible=False)

if SAVE_FIGS:
    FIG_PATH = Path(__file__).parent / 'figures'
    fig.savefig(FIG_PATH / f"graph_path_lengths_V{V}.pdf")

plt.show()

# =============================================================================
# =============================================================================
