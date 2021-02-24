#!/usr/bin/env python3
# =============================================================================
#     File: bst_study.py
#  Created: 2021-02-22 15:13
#   Author: Bernie Roesler
#
r"""
  Description: Ex 3.2.39 and 3.2.40. Tests of number of compares for search
    hits and search misses in a BST, as compared to the theoretical value::

        2 log N + 2 \gamma = 3 \approx 1.39 log N - 1.85

    where $\gamma = 0.57721...$ is *Euler's constant*.

    Estimates the average BST height for multiple values of N, as compared to
    the theoretical value::

        2.99 log N.
"""
# =============================================================================

import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from pathlib import Path
from tqdm import tqdm

from algs.search import BST

SAVE_FIGS = True
FORCE_UPDATE = False
PICKLE_FILE = Path('./pkl/bst_compares_1e4.pkl')


def bst_avg_compares(N):
    r"""Theoretical value of average number of compares in a BST.

    From theory, the value is given by::

        2 log N + 2 \gamma - 3 \approx 1.39 log N - 1.85

    where $\gamma = 0.57721...$ is *Euler's constant*.

    Parameters
    ----------
    N : int
        Number of items in the BST.

    Returns
    -------
    result : float
        Expected average number of compares per search in a BST of size `N`.
    """
    return 2*np.log2(N) + 2*np.euler_gamma - 3


def bst_height(N):
    """Theoretical height of BST of size `N`."""
    return 2.99 * np.log2(N)


# Seed the rng for consistency
rng = np.random.default_rng(seed=565656)

N_trials = 1000
# ops = [int(x) for x in [1e2, 1e3, 1e4]]  # number of set operations
ops = [int(x) for x in np.logspace(2, 4)]
M = len(ops)

if FORCE_UPDATE or not PICKLE_FILE.exists():
    # Insert N random (with replacement) keys into an initially empty tree
    cols = pd.MultiIndex.from_product([
            ['compares', 'height', 'path lengths'],
            ['Experiment', 'Theory'],
            ['Avg', 'Std'],
        ])
    df = pd.DataFrame(index=ops, columns=cols)

    # Run the experiments
    comps   = np.empty((N_trials, M))
    heights = np.empty((N_trials, M))
    ipls    = np.empty((N_trials, M))
    for j, N in enumerate(ops):
        print(f"N = {N}...")
        for i in tqdm(range(N_trials)):
            st = BST()
            tot_comp = 0
            for k in rng.integers(N, size=N):
                st[k] = 1  # set a arbitrary value
                tot_comp += st._cost

            # Store stats for averages
            comps[i, j] = tot_comp / N  # cost of building tree of size N
            heights[i, j] = st.height   # height of tree of size N
            ipls[i, j] = st.internal_path_length / N + 1

        df.loc[N, ('compares', 'Experiment')] = comps[:, j].mean(), comps[:, j].std()
        df.loc[N, ('compares', 'Theory')]     = bst_avg_compares(N), None
        df.loc[N, ('height', 'Experiment')]   = heights[:, j].mean(), heights[:, j].std()
        df.loc[N, ('height', 'Theory')]       = bst_height(N), None
        df.loc[N, ('path lengths', 'Experiment')] = ipls[:, j].mean(), ipls[:, j].std()
        df.loc[N, ('path lengths', 'Theory')]     = bst_avg_compares(N), None

    with open(PICKLE_FILE, 'wb') as fp:
        pickle.dump((comps, heights, ipls, df), fp)

else:
    # read data from file
    with open(PICKLE_FILE, 'rb') as fp:
        (comps, heights, ipls, df) = pickle.load(fp)

# print(df)

# -----------------------------------------------------------------------------
#         Make Plots
# -----------------------------------------------------------------------------
# Organize the data for plotting
tf = pd.DataFrame(data=ipls, columns=ops)
tf.index.name = 'trial'
tf.columns.name = 'N'
tf = tf.melt(ignore_index=False).reset_index()
g = tf.drop('trial', axis=1).groupby('N').agg(['mean', 'std'])

# Theory curve
x = np.logspace(np.log10(min(ops)), np.log10(max(ops)))
theory_avg_ipl = 1.39 * np.log2(x) - 1.85

fig = plt.figure(1, clear=True)
ax = fig.add_subplot()

# TODO 
#   * `x_jitter` argument does nothing (per seaborn docs)
#   * would like to plot std at each N
#   * make this plot manually?
# FIXME Why is experimental data ~ 60% of expected height?
#   * plot on p 423 in book is actually *compares* not *path length*. Compares
#   will be larger than path length because there are 2 compares for each
#   right-ward movement or found key, vs a single edge in the path.

# Plot the runtime distributions
sns.scatterplot(ax=ax, data=tf, x='N', y='value',
                color=0.5*np.ones(3), x_jitter=1.0, alpha=0.25)

# Plot the means and stds of each group
sns.scatterplot(ax=ax, data=g['value'], x='N', y='mean',
                color='k', marker='d', s=50)

ax.plot(x, theory_avg_ipl, color='C3', ls='-', marker='.')

# Place labels on axis (like ticklabels)
ax.set_xlabel('operations')
ax.xaxis.set_label_coords((np.max(ops) - np.min(ops))/2, 0,
                           transform=ax.xaxis.get_ticklabels()[0].get_transform())

ax.set_ylabel('compares')
ax.yaxis.set_label_coords(0, np.max(ipls)/2,
                          transform=ax.yaxis.get_ticklabels()[0].get_transform())

ax.annotate(rf"$\leftarrow$ {theory_avg_ipl[-1]:.0f}",
            xy=(max(ops) + 100, theory_avg_ipl[-1]),
            ha='left', va='center', color='C3')

ax.xaxis.label.set_color('C3')
ax.yaxis.label.set_color('C3')
# ax.set_xlim([0, max(ops)])
# ax.set_ylim([0, round(np.max(ipls))])
ax.set_xticks([min(ops), max(ops)])
ax.set_yticks([0, round(np.max(ipls))])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

fig.tight_layout()

if SAVE_FIGS:
    figname = Path(f"./figures/BST_avg_length.pdf")
    fig.savefig(figname)

plt.show()

# =============================================================================
# =============================================================================
