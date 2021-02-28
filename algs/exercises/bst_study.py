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
from scipy.optimize import curve_fit
from tqdm import tqdm

from algs.search import BST

FORCE_UPDATE = False
SAVE_FIGS = False

PICKLE_FILE = Path('./pkl/bst_compares_1e4.pkl')
# PICKLE_FILE = Path('./pkl/bst_compares_tiny.pkl')


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
# ops = [int(x) for x in [1e2, 1e3, 1e4]]
ops = [int(x) for x in np.logspace(2, 4)]
M = len(ops)

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
            # st = BST.fromkeys(rng.choice(N, size=N, replace=False))
            st = BST()
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
        # df.loc[N, ('compares', 'Theory')]     = bst_avg_compares(N), None
        # df.loc[N, ('height', 'Experiment')]   = heights[:, j].mean(), heights[:, j].std()
        # df.loc[N, ('height', 'Theory')]       = bst_height(N), None
        # df.loc[N, ('path lengths', 'Experiment')] = ipls[:, j].mean(), ipls[:, j].std()
        # df.loc[N, ('path lengths', 'Theory')]     = bst_avg_compares(N), None

    with open(PICKLE_FILE, 'wb') as fp:
        pickle.dump((comps, heights, ipls), fp)

else:
    # read data from file
    with open(PICKLE_FILE, 'rb') as fp:
        (comps, heights, ipls) = pickle.load(fp)

# print(df)

# -----------------------------------------------------------------------------
#         Organize the data for plotting
# -----------------------------------------------------------------------------
# TODO plot each of ipls, comps, heights in one set of subplots.
data = ipls
col_name = 'ipls'

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
theory_avg_ipl = bst_avg_compares(x)
approx_avg_ipl = 1.39 * np.log2(x) - 1.85
theory_avg_height = 2.99 * np.log2(x)

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

if col_name == 'ipls':
    ax.plot(x, approx_avg_ipl, color='C3', ls='-', label=r'$1.39 \lg N - 1.85$')
    ax.annotate(rf"$\leftarrow$ {approx_avg_ipl[-1]:.0f}",
                xy=(max(ops) + 100, approx_avg_ipl[-1]),
                ha='left', va='center', color='C3')

elif col_name == 'comps':
    ax.plot(x, theory_avg_ipl, color='C3', ls='-.', label=r'$2 \lg N + 2\gamma - 3$')
    # Label final values
    ax.annotate(rf"$\leftarrow$ {theory_avg_ipl[-1]:.0f}",
                xy=(max(ops) + 100, theory_avg_ipl[-1]),
                ha='left', va='center', color='C3')

else: # col_name == 'heights':
    ax.plot(x, theory_avg_height, color='C3', ls='--', label=r'$2.99 \lg N$')
    ax.annotate(rf"$\leftarrow$ {theory_avg_height[-1]:.0f}",
                xy=(max(ops) + 100, theory_avg_height[-1]),
                ha='left', va='center', color='C3')

ax.annotate(rf"$\leftarrow$ {func(x, *popt)[-1]:.0f}",
            xy=(max(ops) + 100, func(x, *popt)[-1]),
            ha='left', va='center', color='k')

# Plot the runtime distributions
sns.scatterplot(ax=ax, data=tf, x='N', y=col_name,
                color=0.5*np.ones(3), s=10, alpha=0.25)

# Plot the means and stds of each group
sns.scatterplot(ax=ax, data=g, x='N', y='mean',
                color='k', marker='d', s=30, zorder=3)

for N, m in g.iterrows():
    ax.plot((N, N), (m['mean'] - m['std'], m['mean'] + m['std']), 
               c='k', ls='-', lw=1, alpha=0.9)

ax.legend(loc='lower right')

# Format axes
xlim = ax.get_xlim()
ylim = ax.get_ylim()

ax.xaxis.label.set_color('C3')
ax.yaxis.label.set_color('C3')
# ax.set_xlim([0, max(ops)])
# ax.set_ylim([0, round(np.max(ipls))])
ax.set_xticks([min(ops), max(ops)])
# ax.set_yticks([0, round(np.max(ipls) / 10) * 10])
ax.set_yticks([0, round(ylim[1])])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Place labels on axis (like ticklabels)
ax.set_xlabel('operations')
# ax.xaxis.set_label_coords((np.max(ops) - np.min(ops))/2, 0,
#                           transform=ax.xaxis.get_ticklabels()[0].get_transform())
ax.xaxis.set_label_coords(np.mean(xlim), 0,
                          transform=ax.xaxis.get_ticklabels()[0].get_transform())

ax.set_ylabel('compares')
ax.yaxis.set_label_coords(0, ylim[1] / 2,
                          transform=ax.yaxis.get_ticklabels()[0].get_transform())

fig.tight_layout()

if SAVE_FIGS:
    # figname = Path('./figures/BST_avg_length.pdf')
    figname = Path('./figures/BST_avg_compares.pdf')
    fig.savefig(figname)

plt.show()

# =============================================================================
# =============================================================================
