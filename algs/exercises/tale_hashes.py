#!/usr/bin/env python3
# =============================================================================
#     File: tale_hashes.py
#  Created: 2022-04-21 22:00
#   Author: Bernie Roesler
#
"""
  Description: Plot hash values of Tale of Two Cities.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import re

from pathlib import Path
from tqdm import tqdm

filename = Path('../data/tale.txt')

# split on non-alphabet chars and underscores
pat = re.compile(r"[a-zA-Z']+")

M = 97  # choose a prime
hashes = list()


def hash_code(x):
    return hash(x) % M


def count_lines(fp):
    """Scan through file to count the number of lines."""
    for i, line in enumerate(fp, 1):
        pass
    fp.seek(0)  # rewind file
    return i



with open(filename, 'r') as fp:
    # for line in tqdm(fp, total=count_lines(fp)):
    for line in fp:
        hashes.extend([hash_code(word) for word in pat.findall(line.lower())])

# Generate known uniform distribution of integers for comparison
rng = np.random.default_rng(seed=56)
rands = rng.random(size=len(hashes))
rand_ints = np.r_[[hash_code(x) for x in rands]]

# ----------------------------------------------------------------------------- 
#         Plots
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True)
ax = fig.add_subplot()
ax.hist(rand_ints, bins=M, rwidth=0.9, color='C0', alpha=0.4)

n, _, _ = ax.hist(hashes, bins=M, rwidth=0.9, color='k')
m = int(np.mean(n))  # bar height
ax.axhline(m, lw=1, color='C3')
ax.annotate(fr"${m} \approx {len(hashes)} / {M}$",
            xy=(5, m), xycoords='data',
            xytext=(0.01, 0.30), textcoords='axes fraction',
            ha='left', va='top', color='C3',
            arrowprops=dict(edgecolor='none',
                            facecolor='C3',
                            shrink=0.01,
                            width=2,
                            headwidth=7)
            )

# Format the plot
ax.set(xlabel='key value',
       ylabel='frequency')

ax.set_xlim([0, M-1])
ax.set_xticks([0, M-1])
ax.set_xticklabels([0, M-1])

ax.set_yticks([])
ax.set_yticklabels([])

ax.xaxis.label.set_color('C3')
ax.yaxis.label.set_color('C3')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.grid(None)

plt.show()

# =============================================================================
# =============================================================================
