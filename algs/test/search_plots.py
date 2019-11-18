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

from algs.search import SequentialSearchST, BinarySearchST
from test_search import FrequencyCounter

# Choose symbol table to test
ST_name = 'SequentialSearchST'
# ST_name = 'BinarySearchST'

# filename = 'data/tiny_tale.txt'  # 292
filename = 'data/tale.txt'       # 779K
# filename = 'data/leipzig1m.txt'  # 124M

minlen = 8
tag = os.path.splitext(os.path.basename(filename))[0]

# Load the FrequencyCounter
fc = pickle.load(open(f"./pkl/{tag}_{ST_name}_m{minlen:02d}.pkl", 'rb'))

ops = np.arange(fc.N)  # one operation per word in input
mean_cmp = np.cumsum(fc.cost)[1:] / ops[1:]  # cumulative average cost

# Plot the amortized cost (# cost) vs. number of `put` operations
fig = plt.figure(1, clear=True)
ax = fig.add_subplot()
ax.set(title=f"{ST_name}: {os.path.basename(filename)}, minlen={minlen}",
       xlabel='operations',
       ylabel='cost')

ax.scatter(ops, fc.cost, c=0.7*np.array([[1, 1, 1]]), s=1, alpha=0.8)
ax.plot(ops[1:], mean_cmp, 'C3-')

ax.text(fc.N, 0.99*mean_cmp[-1], f"$\leftarrow$ {mean_cmp[-1]:.0f}", color='C3')
ax.xaxis.label.set_color('C3')
ax.yaxis.label.set_color('C3')
ax.set_xlim([0, fc.N])
ax.set_ylim([0, np.max(fc.cost)])
ax.set_xticks([0, fc.N])
ax.set_yticks([0, np.max(fc.cost)])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()

plt.show()

# =============================================================================
# =============================================================================
