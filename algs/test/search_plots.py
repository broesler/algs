#!/usr/bin/env python3
# =============================================================================
#     File: search_plots.py
#  Created: 2019-11-16 12:59
#   Author: Bernie Roesler
#
"""
  Description: Plot amortized cost of various types of searches.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import os
import pickle

from matplotlib.gridspec import GridSpec

from algs.search import SequentialSearchST, BinarySearchST
from frequency_counter import FrequencyCounter

# filename = 'data/tiny_tale.txt'  # 292
filename = 'data/tale.txt'       # 779K
# filename = 'data/leipzig1m.txt'  # 124M

tag = os.path.splitext(os.path.basename(filename))[0]

minlen = 8

fig = plt.figure(0, figsize=(12, 6), clear=True)
fig.suptitle(f"{os.path.basename(filename)}, minlen={minlen}", y=0.99)
gs = GridSpec(nrows=1, ncols=2)

pad = 5  # position labels

for i, ST_name in enumerate(['SequentialSearchST', 'BinarySearchST']):
    # Load the FrequencyCounter
    fc = pickle.load(open(f"./pkl/{tag}_{ST_name}_m{minlen:02d}.pkl", 'rb'))

    ops = np.arange(fc.N)  # one operation per word in input
    mean_cmp = np.cumsum(fc.cost)[1:] / ops[1:]  # cumulative average cost

    # Plot the amortized cost (# cost) vs. number of `put` operations
    ax = fig.add_subplot(gs[i])
    ax.set_title(ST_name, fontsize=12)
    ax.set(xlabel='operations',
           ylabel='cost')

    ax.scatter(ops, fc.cost, c=0.7*np.array([[1, 1, 1]]), s=1, alpha=0.8)
    ax.plot(ops[1:], mean_cmp, 'C3-')

    ax.annotate(f"$\leftarrow$ {mean_cmp[-1]:.0f}", 
                xy=(fc.N, mean_cmp[-1]),
                ha='left', va='center', color='C3')
    ax.xaxis.label.set_color('C3')
    ax.yaxis.label.set_color('C3')
    ax.set_xlim([0, fc.N])
    ax.set_ylim([0, np.max(fc.cost)])
    ax.set_xticks([0, fc.N])
    ax.set_yticks([0, np.max(fc.cost)])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

gs.tight_layout(fig)

plt.show()

# =============================================================================
# =============================================================================
