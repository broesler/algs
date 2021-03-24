#!/usr/bin/env python3
# =============================================================================
#     File: bst_study.py
#  Created: 2021-02-22 15:13
#   Author: Bernie Roesler
#
r"""
  Description: Ex 3.2.39 and 3.2.40. Tests of number of compares for search
    hits and search misses in a BST, as compared to the theoretical value::

        2 lg N + 2 \gamma = 3 \approx 1.39 lg N - 1.85

    where $\gamma = 0.57721...$ is *Euler's constant*.

    Estimates the average BST height for multiple values of N, as compared to
    the theoretical value::

        2.99 lg N.

    This study also incorporates Ex 3.3.43, 3.3.44, and 3.3.46 to compare BSTs
    with RedBlackBSTs. In a 2-3 tree, the expected average search time is::

        lg N - 0.5

    and the expected height is::

        1.0 lg N.
"""
# =============================================================================

import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from pathlib import Path
from scipy.optimize import curve_fit
from tqdm import tqdm

from algs.search import BST, RedBlackBST

FORCE_UPDATE = False
SAVE_FIGS = False

# Seed the rng for consistency
rng = np.random.default_rng(seed=565656)

N_trials = 1000
# ops = [int(x) for x in [1e2, 1e3, 1e4]]
ops = [int(x) for x in np.logspace(2, 4)]
M = len(ops)

# for ST, tag in zip([BST, RedBlackBST], ['bst', 'rbst']):
for ST, tag in zip([RedBlackBST], ['rbst']):
# for ST, tag in zip([BST], ['bst']):
    PICKLE_FILE = Path(f"./pkl/{tag}_compares_1e4.pkl")
    # PICKLE_FILE = Path(f"./pkl/{tag}_compares_tiny.pkl")

    if FORCE_UPDATE or not PICKLE_FILE.exists():
        # Insert N random (with replacement) keys into an initially empty tree
        # cols = pd.MultiIndex.from_product([
        #         ['compares', 'height', 'path lengths'],
        #         ['Experiment', 'Theory'],
        #         ['Avg', 'Std'],
        #     ])
        # df = pd.DataFrame(index=ops, columns=cols)

        # Run the experiments
        comps   = np.empty((N_trials, M))
        heights = np.empty((N_trials, M))
        ipls    = np.empty((N_trials, M))
        for j, N in enumerate(ops):
            print(f"N = {N}...")
            for i in tqdm(range(N_trials)):
                st = ST()
                tot_comp = 0
                for k in rng.choice(N, size=N, replace=False):
                    st[k] = 1  # set an arbitrary value
                    tot_comp += st._cost

                # Store stats for averages
                comps[i, j] = tot_comp / N  # cost of building tree of size N
                heights[i, j] = st.height   # height of tree of size N
                ipls[i, j] = st.internal_path_length / N + 1

            # Prep summary table
            # TODO combine matrices into one big df and use that instead.
            # df.loc[N, ('compares', 'Experiment')] = comps[:, j].mean(), comps[:, j].std()
            # df.loc[N, ('compares', 'Theory')]     = bst_avg_comps(N), None
            # df.loc[N, ('height', 'Experiment')]   = heights[:, j].mean(), heights[:, j].std()
            # df.loc[N, ('height', 'Theory')]       = bst_height(N), None
            # df.loc[N, ('path lengths', 'Experiment')] = ipls[:, j].mean(), ipls[:, j].std()
            # df.loc[N, ('path lengths', 'Theory')]     = bst_avg_comps(N), None

        with open(PICKLE_FILE, 'wb') as fp:
            pickle.dump((comps, heights, ipls), fp)

    else:
        # TODO read each file separately
        # read data from file
        with open(PICKLE_FILE, 'rb') as fp:
            (comps, heights, ipls) = pickle.load(fp)

# print(df)

# -----------------------------------------------------------------------------
#         Organize the data for plotting
# -----------------------------------------------------------------------------
# TODO
#   * plot each of ipls, comps, heights in one set of subplots.
#   * compare BST with RedBlackBST
data = ipls
col_name = 'ipls'
# data = comps
# col_name = 'comps'
# data = heights
# col_name = 'heights'

tf = pd.DataFrame(data=data, columns=ops)
tf.index.name = 'trial'
tf.columns.name = 'N'
tf = (tf.melt(ignore_index=False)
        .reset_index()
        .rename(columns={'value': col_name})
      )

# Aggregate the meand and std
g = (tf.drop('trial', axis=1)
       .groupby('N')
       .agg(['mean', 'std'])
       .droplevel(0, axis=1)
     )

# Theory curve
x = np.logspace(np.log10(min(ops)), np.log10(max(ops)))

# Fit curve to data
def func(x, a, b):
    return a * np.log2(x) + b

popt, pcov = curve_fit(func, g.index, g['mean'])
# print(popt)

# -----------------------------------------------------------------------------
#         Make Plots
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True)
ax = fig.add_subplot()

# Plot the theoretical curves, and the curve fit to the data
ax.plot(x, func(x, *popt), color='k', ls='-',
        label=fr"${popt[0]:.2f} \lg N {popt[1]:+.2f}$")
ax.annotate(rf"$\leftarrow$ {func(x, *popt)[-1]:.0f}",
            xy=(max(ops) + 100, func(x, *popt)[-1]),
            ha='left', va='center', color='k')

theory_dict = dict(bst_avg_comps=lambda N: 2*np.log2(N) + 2*np.euler_gamma - 3,
                   bst_avg_ipls=lambda N: 1.39 * np.log2(N) - 1.85,
                   bst_heights=lambda N: 2.99 * np.log2(N),
                   rbst_avg_comps=lambda N: np.log2(N) - 0.5,
                   # rbst_avg_comps=lambda N: 1.39 * np.log2(N) - 1.85,
                   rbst_avg_ipls=lambda N: np.log2(N) - 0.5,
                   rbst_avg_heights=lambda N: np.log2(N) - 0.5
                   )
# LaTeX labels for the theory curves
labels_dict = dict(bst_avg_comps=r'$2 \lg N + 2\gamma - 3$',
                   bst_avg_ipls=r'$1.39 \lg N - 1.85$',
                   bst_heights=r'$2.99 \lg N$',
                   rbst_avg_comps=r'$\lg N - 0.5$',
                   # rbst_avg_comps=r'$1.39 \lg N - 1.85$',
                   rbst_avg_ipls=r'$\lg N - 0.5$',
                   rbst_avg_heights=r'$\lg N - 0.5$'
                   )

y_theory = theory_dict[f"{tag}_avg_{col_name}"](x)
label = labels_dict[f"{tag}_avg_{col_name}"]

ax.plot(x, y_theory, color='C3', ls='-', label=label)
ax.annotate(rf"$\leftarrow$ {y_theory[-1]:.0f}",
            xy=(max(ops) + 100, y_theory[-1]),
            ha='left', va='center', color='C3')

# Plot the runtime distributions
sns.scatterplot(ax=ax, data=tf, x='N', y=col_name,
                color=0.5*np.ones(3), s=10, alpha=0.10)

# g['mean'] *= 3/4  # FIXME compares are too large by 1/4-ish -> EXCLUDE multiple compares in 3-nodes
# g['mean'] *= 3/4  # FIXME heights are too large by 1/3 (for counting all nodes)
# g['mean'] *= 4/3  # FIXME heights are too small by 1/3 (for counting only black nodes)
# Plot the means and stds of each group
sns.scatterplot(ax=ax, data=g, x='N', y='mean',
                color='k', marker='d', s=30, zorder=3)

for N, m in g.iterrows():
    ax.plot((N, N), (m['mean'] - m['std'], m['mean'] + m['std']),
               c='k', ls='-', lw=2, alpha=1.0)

ax.legend(loc='lower right')

# Format axes
xlim = ax.get_xlim()
ylim = [0, 20] #ax.get_ylim()

ax.ticklabel_format(style='plain')  # no scientific notation
ax.xaxis.label.set_color('C3')
ax.yaxis.label.set_color('C3')
ax.set_xticks([min(ops), max(ops)])
ax.set_yticks([0, round(ylim[1])])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(False)

# Place labels on axis (like ticklabels)
ax.set_xlabel('operations', fontweight='bold')
ax.xaxis.set_label_coords(np.mean(xlim), 0,
                          transform=ax.xaxis.get_ticklabels()[0].get_transform())

ax.set_ylabel(col_name, fontweight='bold')
ax.yaxis.set_label_coords(0, ylim[1] / 2,
                          transform=ax.yaxis.get_ticklabels()[0].get_transform())

fig.tight_layout()

if SAVE_FIGS:
    # figname = Path('./figures/BST_avg_length.pdf')
    figname = Path('./figures/bst_avg_comps.pdf')
    fig.savefig(figname)

plt.show()

# =============================================================================
# =============================================================================
