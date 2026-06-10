#!/usr/bin/env python3
# =============================================================================
#     File: separate_chaining_distribution.py
#  Created: 2022-04-26 20:51
#   Author: Bernie Roesler
# =============================================================================

r"""Exercise 3.4.36: List length range.

Write a program that inserts *N* random int keys into a table of size *N* / 100
using separate chaining, then finds the length of the shortest and longest
lists, for :math:`N = 10^3, 10^4, 10^5, 10^6`.
"""

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from algs.search.hash import SeparateChainingHashST

rng = np.random.default_rng(seed=56)

# Insert N random non-negative integers into a table of size N/100.
# Ns = [10**x for x in range(3, 7)]  # book values
Ns = [10**x for x in range(3, 5)]  # book values
α = 100

min_Ls = []
max_Ls = []

for N in tqdm(Ns):
    M = N // α  # table size

    keys = rng.integers(N * N, size=N)
    st = SeparateChainingHashST.fromkeys(keys, M=M, resize=False)

    counts = np.array(st._list_lengths())
    min_Ls.append(counts.min())
    max_Ls.append(counts.max())

min_Ls = np.r_[min_Ls]
max_Ls = np.r_[max_Ls]

# -----------------------------------------------------------------------------
#         Plot
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(num=1, clear=True)

ax.axhline(α, c="tab:blue", ls="--", label='α = N/M')
ax.scatter(Ns, max_Ls, c='tab:blue', label='max length')
ax.scatter(Ns, min_Ls, c='tab:blue', marker='s', alpha=0.5, label='min length')

ax.legend()
ax.set(
    title='Max/Min List Length vs N',
    xlabel='N',
    ylabel='Longest List',
    xscale='log',
)

plt.show()

# =============================================================================
# =============================================================================
