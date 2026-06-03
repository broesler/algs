#!/usr/bin/env python3
# =============================================================================
#     File: search_plots.py
#  Created: 2019-11-16 12:59
#   Author: Bernie Roesler
# =============================================================================

"""Plot amortized cost of various types of searches."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# import seaborn.objects as so

DATA_PATH = Path(__file__).parent.parent / 'data'
PKL_PATH = Path(__file__).parent / 'pkl' / 'frequency_count'

SAVE_FIGS = False

MINLEN = 8  # 1, 8, 10

# filestem = 'tiny_tale'  # 292
filestem = 'tale'  # 779K
# filestem = 'leipzig1m'  # 124M

# Choose which parameter sets to plot: (ST_name, kind)
params = [
    ('ArrayST', 'append'),
    # ('ArrayST', 'append_selforg'),
    # ('ArrayST', 'insert'),
    # ('ArrayST', 'insert_selforg'),
    ('BinarySearchST', ''),
    # ('BST', ''),
    ('RedBlackBST', ''),
    ('LinearProbingHashST', ''),
    # ('SeparateChainingHashST', 'Seq'),
    # ('SeparateChainingHashST', 'resize_Seq'),
]

# Load the summary data
df = pd.read_parquet(PKL_PATH / "frequency_count_summary.parquet")
df['kwargs'] = df['kwargs'].map(json.loads)

# Filter for these particular (minlen, filestem, ST_names) combinations
pf = df.loc[(df['minlen'] == MINLEN) & (df['filestem'] == filestem)]


def make_label(tf):
    """Make a label for the plot like "Array(append=True, selforg=False)"."""
    kw_str = ', '.join(f"{k}={v}" for k, v in tf['kwargs'].items())
    return f"{ST_name}({kw_str})" if kw_str else ST_name


# -----------------------------------------------------------------------------
#         Plot amortized cost of each search type
# -----------------------------------------------------------------------------
fig, axs = plt.subplots(num=0, nrows=len(params), sharex=True, clear=True)
fig.set_size_inches((6.4, min(8, max(4.8, 3 * len(params)))), forward=True)
fig.suptitle(f"{filestem}.txt, min. length = {MINLEN}")

for ax, (ST_name, kind) in zip(axs.flat, params):
    # Get the individual row for this (minlen, filestem, ST_name, kind)
    tf = pf.loc[(pf['alg'] == ST_name) & (pf['kind'] == kind)]

    if len(tf) != 1:
        raise ValueError(f"Expected exactly one row for {ST_name}, got {len(tf)}")

    tf = tf.iloc[0]

    # Load the data
    data = np.load(tf['trace_file'])
    cost, time = data['cost'], data['time']

    ops = np.arange(tf['words'])  # one operation per word in input
    mean_cmp = np.cumsum(cost)[1:] / ops[1:]  # cumulative average cost

    # Plot the amortized cost (# cost) vs. number of `put` operations
    note = make_label(tf)

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
# Choose which parameter sets to plot: (ST_name, kind)
params = [
    ('SequentialSearchST', ''),
    ('ArrayST', 'append'),
    ('ArrayST', 'append_selforg'),
    ('ArrayST', 'insert'),
    ('ArrayST', 'insert_selforg'),
    ('BinarySearchST', ''),
    ('BST', ''),
    ('RedBlackBST', ''),
    ('LinearProbingHashST', ''),
    ('SeparateChainingHashST', 'Seq'),
    ('SeparateChainingHashST', 'resize_Seq'),
    ('SeparateChainingHashST', 'Arr'),
    ('SeparateChainingHashST', 'resize_Arr'),
]


records = []

for ST_name, kind in params:
    # Get the individual row for this (minlen, filestem, ST_name)
    tf = pf.loc[(pf['alg'] == ST_name) & (pf['kind'] == kind)]

    if len(tf) != 1:
        raise ValueError(f"Expected exactly one row for {ST_name}, got {len(tf)}")

    tf = tf.iloc[0]

    # Load the data
    data = np.load(tf['trace_file'])
    ops = np.arange(tf['words'])  # one operation per word in input
    mean_cmp = np.cumsum(data['time'])[1:]  # cumulative runtime

    temp_df = pd.DataFrame(
        {
            'alg': ST_name,
            'kind': kind,
            'label': make_label(tf),
            'ops': ops[1:],
            'mean_time': mean_cmp,
        }
    )

    records.append(temp_df)

tf = pd.concat(records, ignore_index=True)

# Plot the cumulative runtime vs. number of `put` operations
fig, ax = plt.subplots(num=1, clear=True)
fig.suptitle(f"{filestem}.txt, min. length = {MINLEN}")

# Seaborn lineplot
sns.lineplot(
    data=tf,
    x='ops',
    y='mean_time',
    hue='alg',
    style='kind',
    ax=ax,
)

ax.set(xlabel='operations', ylabel='runtime [s]', xscale='log', yscale='log')

if SAVE_FIGS:
    figname = FIG_PATH / f"{fig_stem}_runtime.pdf"
    fig.savefig(figname)

plt.show()

# =============================================================================
# =============================================================================
