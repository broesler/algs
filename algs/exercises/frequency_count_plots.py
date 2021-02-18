#!/usr/bin/env python3
# =============================================================================
#     File:
#  Created: 2019-11-16 12:59
#   Author: Bernie Roesler
#
"""
  Description: Plot amortized cost of various types of searches.
    See pages 377 and 384 in the text for examples.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import pickle

from matplotlib.gridspec import GridSpec
from pathlib import Path

SAVE_FIGS = False
if SAVE_FIGS:
    plt.close('all')

MINLEN = 8

# filename = Path('../data/tiny_tale.txt')  # 292
filename = Path('../data/tale.txt')       # 779K
# filename = Path('../data/leipzig1M.txt')  # 124M

tag = filename.stem

fig = plt.figure(0, figsize=(12, 8), clear=True)
fig.suptitle(f"{filename.name}, minlen={MINLEN}")
gs = GridSpec(nrows=2, ncols=1)

for i, ST_name in enumerate(['SequentialSearchST', 'BinarySearchST']):
    # Load the FrequencyCounter
    fc = pickle.load(open(f"./pkl/{tag}_{ST_name}_m{MINLEN:02d}.pkl", 'rb'))

    ops = np.arange(fc.N)  # one operation per word in input
    mean_cmp = np.cumsum(fc.cost)[1:] / ops[1:]  # cumulative average cost

    # Plot the amortized cost (# cost) vs. number of `put` operations
    ax = fig.add_subplot(gs[i])
    ax.set_title(ST_name, fontsize=12)

    # Place labels on axis (like ticklabels)
    ax.set_xlabel('operations')
    ax.xaxis.set_label_coords(np.mean(ops), 0,
            transform=ax.xaxis.get_ticklabels()[0].get_transform())

    ax.set_ylabel('cost')
    ax.yaxis.set_label_coords(0, max(fc.cost)/2,
            transform=ax.yaxis.get_ticklabels()[0].get_transform())

    ax.scatter(ops, fc.cost, c=0.7*np.array([[1, 1, 1]]), s=1, alpha=0.8)
    ax.plot(ops[1:], mean_cmp, 'C3-')

    ax.annotate(rf"$\leftarrow$ {mean_cmp[-1]:.0f}",
                xy=(fc.N, mean_cmp[-1]),
                ha='left', va='center', color='C3')

    ax.xaxis.label.set_color('C3')
    ax.yaxis.label.set_color('C3')
    ax.set_xlim([0, fc.N])
    ax.set_ylim([0, max(fc.cost)])
    ax.set_xticks([0, fc.N])
    ax.set_yticks([0, max(fc.cost)])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# gs.tight_layout(fig, rect=(0, 0, 1, 0.96))
gs.tight_layout(fig)

if SAVE_FIGS:
    figname = Path(f"./figures/{tag}_M{MINLEN}_frequency_count.pdf")
    fig.savefig(figname)

plt.show()

# =============================================================================
# =============================================================================
