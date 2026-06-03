#!/usr/bin/env python3
# =============================================================================
#     File: search_plots.py
#  Created: 2019-11-16 12:59
#   Author: Bernie Roesler
# =============================================================================

"""Plot amortized cost of various types of searches."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).parent.parent / 'data'
PKL_PATH = Path(__file__).parent / 'pkl'

SAVE_FIGS = False

MINLEN = 8  # 1, 8, 10
kind = 'resize'  # 'ins', 'app', 'selforg', 'cache', 'resize'

# filestem = 'tiny_tale'  # 292
filestem = 'tale'       # 779K
# filestem = 'leipzig1m'  # 124M

ST_names = ['ArrayST', 'BinarySearchST', 'BST', 'RedBlackBST']
# ST_names = ['ArrayST', 'RedBlackBST', 'SeparateChainingHashST']
# ST_names = ['SeparateChainingHashST', 'LinearProbingHashST']

# Load the summary data
df = pd.read_parquet(PKL_PATH / f"frequency_count_summary_{kind}.parquet")
df = df.rename({'file': 'filestem'}, axis=1)

# Filter for these particular (minlen, filestem, ST_names) combinations
df = df.loc[
    (df['minlen'] == MINLEN) & (df['filestem'] == filestem) & (df['alg'].isin(ST_names))
]

# -----------------------------------------------------------------------------
#         Plot amortized cost of each search type
# -----------------------------------------------------------------------------
fig, axs = plt.subplots(num=0, nrows=len(ST_names), sharex=True, clear=True)
fig.set_size_inches((6.4, min(8, max(4.8, 3 * len(ST_names)))), forward=True)
fig.suptitle(f"{filestem}.txt, min. length = {MINLEN}")

for ax, ST_name in zip(axs.flat, ST_names):
    # Get the individual row for this (minlen, filestem, ST_name)
    tf = df.loc[df['alg'] == ST_name]

    if len(tf) != 1:
        raise ValueError(f"Expected exactly one row for {ST_name}, got {len(tf)}")

    tf = tf.iloc[0]

    # Load the data
    data = np.load(tf['trace_file'])
    cost, time = data['cost'], data['time']

    ops = np.arange(tf['words'])  # one operation per word in input
    mean_cmp = np.cumsum(cost)[1:] / ops[1:]  # cumulative average cost

    # Plot the amortized cost (# cost) vs. number of `put` operations
    note = ST_name

    if ST_name == 'SeparateChainingHashST':
        note += f" (M = {tf['M']})"

    ax.annotate(
        note, xy=(0.01, 0.97), xycoords='axes fraction', ha='left', va='top', color='k'
    )

    # Plot
    ax.scatter(ops, cost, c='0.7', s=1, alpha=0.8)
    ax.plot(ops[1:], mean_cmp, c='tab:red')

    ax.annotate(
        rf"$\leftarrow$ {mean_cmp[-1]:.1f}",
        xy=(tf['words'], mean_cmp[-1]),
        ha='left',
        va='center',
        color='tab:red',
    )

    ax.set_ylabel('cost', c='tab:red', labelpad=-15)
    ax.set(
        xlim=[0, tf['words']],
        ylim=[0, max(cost)],
        xticks=[0, tf['words']],
        xticklabels=[0, f"{tf['words']:}"],
        yticks=[0, max(cost)],
    )

    # Place labels on axis (like ticklabels)
    if ax.get_subplotspec().is_last_row():
        ax.set_xlabel('operations', c='tab:red', labelpad=-12)

    ax.spines[['top', 'right']].set_visible(False)


if SAVE_FIGS:
    FIG_PATH = Path(__file__).parent / 'figures'
    fig_stem = f"{filestem}_M{MINLEN:02d}_{kind}"
    figname = FIG_PATH / f"{fig_stem}_frequency_count.pdf"
    fig.savefig(figname)


# -----------------------------------------------------------------------------
#         Plot actual timings
# -----------------------------------------------------------------------------
# ST_names = [
#     'ArrayST',
#     'BinarySearchST',
#     'BST',
#     'ArrayBST',
#     'RedBlackBST',
#     'SeparateChainingHashST',
#     'LinearProbingHashST',
# ]

fig, ax = plt.subplots(num=1, clear=True)
fig.suptitle(f"{filestem}.txt, min. length = {MINLEN}")

for ST_name in ST_names:
    kind = 'resize' if 'hash' in ST_name.lower() else 'app'

    # Get the individual row for this (minlen, filestem, ST_name)
    tf = df.loc[df['alg'] == ST_name]

    if len(tf) != 1:
        raise ValueError(f"Expected exactly one row for {ST_name}, got {len(tf)}")

    tf = tf.iloc[0]

    # Load the data
    data = np.load(tf['trace_file'])
    cost, time = data['cost'], data['time']

    ops = np.arange(tf['words'])  # one operation per word in input
    mean_cmp = np.cumsum(time)[1:]  # cumulative average cost

    # Plot the cumulative runtime vs. number of `put` operations
    ax.plot(ops[1:], mean_cmp, label=ST_name)

# Format the axes
ax.legend()
ax.set(xscale='log', yscale='log')
ax.set_xlabel('operations', c='tab:red')
ax.set_ylabel('time [s]', c='tab:red')
ax.spines[['top', 'right']].set_visible(False)

if SAVE_FIGS:
    figname = FIG_PATH / f"{fig_stem}_runtime.pdf"
    fig.savefig(figname)

plt.show()

# =============================================================================
# =============================================================================
