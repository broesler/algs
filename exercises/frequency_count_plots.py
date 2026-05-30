#!/usr/bin/env python3
# =============================================================================
#     File: search_plots.py
#  Created: 2019-11-16 12:59
#   Author: Bernie Roesler
# =============================================================================

"""Plot amortized cost of various types of searches."""

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# TODO
# * update label coords to just use `labelpad=-15`
# * update `np.array` calls to `np.r_`, etc.

SAVE_FIGS = False

MINLEN = 8  # 1, 8, 10

DATA_PATH = Path(__file__).parent.parent / 'data'
PKL_PATH = Path(__file__).parent / 'pkl'

filename = DATA_PATH / 'tiny_tale.txt'  # 292
# filename = DATA_PATH / 'tale.txt'  # 779K
# filename = DATA_PATH / 'leipzig1m.txt'  # 124M

# ST_names = ['ArrayST', 'BinarySearchST', 'BST', 'RedBlackBST']
# ST_names = ['ArrayST', 'RedBlackBST', 'SeparateChainingHashST']
ST_names = ['SeparateChainingHashST', 'LinearProbingHashST']

tag = filename.stem
kind = 'resize'  # 'ins', 'app', 'selforg', 'cache', 'resize'

fig = plt.figure(0, clear=True)
fig.set_size_inches((6, max(8, 3 * len(ST_names))), forward=True)
fig.suptitle(f"{filename.name}, min. length = {MINLEN}")
gs = fig.add_gridspec(nrows=len(ST_names), ncols=1)

for i, ST_name in enumerate(ST_names):
    # kind = 'resize' if ST_name == 'SeparateChainingHashST' else 'app'

    # Load the FrequencyCounter
    pkl_file = PKL_PATH / f"{tag}_{ST_name}_m{MINLEN:02d}_{kind}.pkl"
    with pkl_file.open('rb') as fp:
        fc = pickle.load(fp)

    ops = np.arange(fc.N)  # one operation per word in input
    mean_cmp = np.cumsum(fc.cost)[1:] / ops[1:]  # cumulative average cost

    # Plot the amortized cost (# cost) vs. number of `put` operations
    ax = fig.add_subplot(gs[i])
    # ax.set_title(ST_name, fontsize=12)
    note = ST_name
    if ST_name == 'SeparateChainingHashST':
        note += f" (M = {fc.t.M})"
    ax.annotate(
        note, xy=(0.01, 0.97), xycoords='axes fraction', ha='left', va='top', color='k'
    )

    # Place labels on axis (like ticklabels)
    ax.set_xlabel('operations')
    ax.xaxis.set_label_coords(
        np.mean(ops), 0, transform=ax.xaxis.get_ticklabels()[0].get_transform()
    )

    ax.set_ylabel('cost')
    ax.yaxis.set_label_coords(
        0, max(fc.cost) / 2, transform=ax.yaxis.get_ticklabels()[0].get_transform()
    )

    ax.scatter(ops, fc.cost, c=0.7 * np.array([[1, 1, 1]]), s=1, alpha=0.8)
    ax.plot(ops[1:], mean_cmp, 'C3-')

    ax.annotate(
        rf"$\leftarrow$ {mean_cmp[-1]:.1f}",
        xy=(fc.N, mean_cmp[-1]),
        ha='left',
        va='center',
        color='C3',
    )

    ax.xaxis.label.set_color('C3')
    ax.yaxis.label.set_color('C3')
    ax.set_xlim([0, fc.N])
    ax.set_ylim([0, max(fc.cost)])
    ax.set_xticks([0, fc.N])
    ax.set_yticks([0, max(fc.cost)])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Hide x-labels except for bottom
    if i < len(ST_names) + 1:
        ax.xaxis.set_ticklabels([])
        ax.set_xlabel('')
    else:
        ax.ticklabel_format(style='plain')  # no scientific notation

# gs.tight_layout(fig, rect=(0, 0, 1, 0.96))
gs.tight_layout(fig)

if SAVE_FIGS:
    FIG_PATH = Path(__file__).parent / 'figures'
    figname = FIG_PATH / f"{tag}_M{MINLEN:02d}_{kind}_frequency_count.pdf"
    fig.savefig(figname)


# -----------------------------------------------------------------------------
#         Plot actual timings
# -----------------------------------------------------------------------------
# ST_names = ['ArrayST', 'BinarySearchST', 'BST', 'ArrayBST', 'RedBlackBST',
#             'SeparateChainingHashST']
ST_names = [
    'ArrayST',
    'BinarySearchST',
    'BST',
    'ArrayBST',
    'RedBlackBST',
    'SeparateChainingHashST',
    'LinearProbingHashST',
]

# tag = filename.stem
# kind = 'app'  # 'ins', 'app', 'selforg', 'cache'

fig = plt.figure(1, clear=True)
fig.suptitle(f"{filename.name}, min. length = {MINLEN}")
ax = fig.add_subplot()

for ST_name in ST_names:
    kind = 'resize' if 'hash' in ST_name.lower() else 'app'

    # Load the FrequencyCounter
    pkl_file = PKL_PATH / f"{tag}_{ST_name}_m{MINLEN:02d}_{kind}.pkl"
    with pkl_file.open('rb') as fp:
        fc = pickle.load(fp)

    ops = np.arange(fc.N)  # one operation per word in input
    mean_cmp = np.cumsum(fc.time)[1:]  # cumulative average cost

    # Plot the cumulative runtime vs. number of `put` operations
    ax.plot(ops[1:], mean_cmp, label=ST_name)

# Format the axes
ax.legend()

# Place labels on axis (like ticklabels)
ax.set(xscale='log', yscale='log')
# ax.set(xscale='log')
ylim = ax.get_ylim()
ax.set_xlabel('operations')
ax.set_ylabel('time [s]')
ax.xaxis.label.set_color('C3')
ax.yaxis.label.set_color('C3')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

fig.tight_layout()

if SAVE_FIGS:
    figname = Path(f"./figures/{tag}_M{MINLEN:02d}_{kind}_runtime.pdf")
    fig.savefig(figname)

plt.show()

# =============================================================================
# =============================================================================
