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

filename = Path('../data/tale.txt')

# split on non-alphabet chars and underscores
pat = re.compile(r"[a-zA-Z']+")

M = 97  # choose a prime

def hash_code(x):
    """Return an integer in [0, M-1]."""
    return hash(x) % M

# Keep track of *unique* words
words = set()

with open(filename, 'r') as fp:
    for line in fp:
        words.update(pat.findall(line.lower()))

N = len(words)
α = N / M

hashes = [hash_code(w) for w in words]

# Generate known uniform distribution of integers for comparison
rng = np.random.default_rng(seed=56)
rand_ints = rng.integers(M, size=len(hashes))

# ----------------------------------------------------------------------------- 
#         Plots
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True, constrained_layout=True)
fig.set_size_inches((8, 2), forward=True)
ax = fig.add_subplot()
ax.hist(rand_ints, bins=M, rwidth=0.9, color='C0', alpha=0.4)

lengths, _, _ = ax.hist(hashes, bins=M, rwidth=0.9, color='k')
m = int(np.mean(lengths))  # bar height == list lengths in hash table
ax.axhline(m, lw=1, color='C3')
ax.annotate(fr"${m} \approx {len(hashes)}~/~{M}$",
            xy=(5, m), xycoords='data',
            xytext=(0.01, 1.05), textcoords='axes fraction',
            ha='left', va='top', color='C3',
            arrowprops=dict(edgecolor='none',
                            facecolor='C3',
                            shrink=0.01,
                            width=1,
                            headwidth=5)
            )

# Format the plot
ax.set(xlabel='key value',
       ylabel='frequency',
       xlim=[0, M-1],
       xticks=[0, M-1],
       xticklabels=[0, M-1],
       yticks=[],
       yticklabels=[]
       )

ax.xaxis.labelpad=-12  # shift label up to fit
ax.yaxis.labelpad=5
ax.xaxis.label.set_color('C3')
ax.yaxis.label.set_color('C3')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

ax.grid(None)

plt.show()

# =============================================================================
# =============================================================================
