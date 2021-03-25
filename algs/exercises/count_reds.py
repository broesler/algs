#!/usr/bin/env python3
# =============================================================================
#     File: exercises/count_reds.py
#  Created: 2021-03-25 12:28
#   Author: Bernie Roesler
#
r"""
  Description: Ex 3.3.42 and 3.3.45. Compute the percentage of red nodes in
  a given red-black BST, and count the number of rotations and node splits used
  to build the tree.
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

from algs.search import RedBlackBST

FORCE_UPDATE = False
SAVE_FIGS = False

# N_trials = 1000
N_trials = 30
ops = [int(x) for x in [1e2, 1e3, 1e4]]
# ops = [int(x) for x in np.logspace(2, 4)]
M = len(ops)

# pickle_file = Path(f"./pkl/rbst_reds_1e4.pkl")
pickle_file = Path(f"./pkl/rbst_reds_tiny.pkl")

if FORCE_UPDATE or not pickle_file.exists():
    # Seed the rng for consistency
    rng = np.random.default_rng(seed=565656)

    # Run the experiments
    reds   = np.empty((N_trials, M))
    rotations = np.empty((N_trials, M))
    splits    = np.empty((N_trials, M))
    for j, N in enumerate(ops):
        print(f"N = {N}...")
        for i in tqdm(range(N_trials)):
            st = RedBlackBST.fromkeys(rng.random(N))
            # Store stats for averages
            reds[i, j] = st.Nred
            rotations[i, j] = st.Nrotations
            splits[i, j] = st.Nsplits

    with open(pickle_file, 'wb') as fp:
        print(f"Writing to '{pickle_file}'...")
        pickle.dump((reds, rotations, splits), fp)

# -----------------------------------------------------------------------------
#         Plots
# -----------------------------------------------------------------------------
opts = dict(reds=dict(ylim=20, ylabel='# red nodes'),
            rotations=dict(ylim=40, ylabel='# rotations'),
            splits=dict(ylim=20, ylabel='# splits'))

fig = plt.figure(1, clear=True)
# fig.set_size_inches((8, 8), forward=True)
gs = fig.add_gridspec(nrows=3, ncols=1)

# pickle_file = Path(f"./pkl/rbst_compares_1e4.pkl")
pickle_file = Path(f"./pkl/rbst_compares_tiny.pkl")
with open(pickle_file, 'rb') as fp:
    reds, rotations, splits = pickle.load(fp)

for i, (data, col_name) in enumerate(zip([reds, rotations, splits],
                                         ['reds', 'rotations', 'splits'])):

    # Organize data
    tf = pd.DataFrame(data=data, columns=ops)
    tf.index.name = 'trial'
    tf.columns.name = 'N'
    tf = (tf.melt(ignore_index=False)
            .reset_index()
            .rename(columns={'value': col_name})
        )

    # Aggregate the mean and std
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
    ax = fig.add_subplot(gs[i])

    # Plot the curve fit to the data
    ax.plot(x, func(x, *popt), color='k', ls='-',
            label=fr"${popt[0]:.2f} \lg N {popt[1]:+.2f}$")
    ax.annotate(rf"$\leftarrow$ {func(x, *popt)[-1]:.0f}",
                xy=(max(ops) + 100, func(x, *popt)[-1]),
                ha='left', va='center', color='k')

    # Plot the runtime distributions
    sns.scatterplot(ax=ax, data=tf, x='N', y=col_name,
                    color=0.5*np.ones(3), s=10, alpha=0.10)

    # Plot the means and stds of each group
    sns.scatterplot(ax=ax, data=g, x='N', y='mean',
                    color='k', marker='d', s=30, zorder=3)

    for N, m in g.iterrows():
        ax.plot((N, N), (m['mean'] - m['std'], m['mean'] + m['std']),
                c='k', ls='-', lw=2, alpha=1.0)

    ax.legend(loc='lower right')

    # Format axes
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    # ylim = [0, opts[col_name]['ylim']]

    ax.xaxis.label.set(color='C3')
    ax.yaxis.label.set(color='C3')
    ax.set_xticks([min(ops), max(ops)])
    ax.set_yticks([0, round(ylim[1])])

    # Place labels on axis (like ticklabels)
    ax.set_xlabel('operations')
    ax.xaxis.set_label_coords(np.mean(xlim), 0,
                            transform=ax.xaxis.get_ticklabels()[0].get_transform())

    ax.set_ylabel(opts[col_name]['ylabel'])
    ax.yaxis.set_label_coords(0, ylim[1] / 2,
                            transform=ax.yaxis.get_ticklabels()[0].get_transform())

    # Hide x-labels except for bottom
    if i < 2:
        ax.xaxis.set_ticklabels([])
        ax.set_xlabel('')
    else:
        ax.ticklabel_format(style='plain')  # no scientific notation

    
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    gs.tight_layout(fig)

    if SAVE_FIGS:
        figname = Path(f"./figures/rbst_avg_{col_name}.pdf")
        fig.savefig(figname)

    plt.show()

# =============================================================================
# =============================================================================
