#!/usr/bin/env python3
# =============================================================================
#     File: double_hashing_compare.py
#  Created: 2022-05-23 17:55
#   Author: Bernie Roesler
#
"""
Plot the frequency distribution of list lengths to compare a single hash with
linear probing with a double hash index update.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path
from scipy.stats import expon

from algs.search import LinearProbingHashST, DoubleHashingHashST
from frequency_counter import FrequencyCounter

MINLEN = 8  # 1, 8, 10
filename = Path('../data/tale.txt')  # 779K

# -----------------------------------------------------------------------------
#         Plot
# -----------------------------------------------------------------------------
fig = plt.figure(0, clear=True, constrained_layout=True)
fig.set_size_inches((8, 6), forward=True)
ax = fig.add_subplot()

for ST, c in zip([LinearProbingHashST, DoubleHashingHashST], ['k', 'C3']):
    # Add each of the unique words in Tale of Two Cities to the hash table.
    fc = FrequencyCounter(ST)
    fc.count_frequencies(filename, MINLEN)
    a = np.r_[fc.t._cluster_lengths()]

    # Plot the histogram of cluster lengths
    bins = np.arange(a.max())+0.5
    freqs, _, _ = ax.hist(a, bins=bins, density=True, rwidth=0.9, color=c,
                          alpha=0.8, label=ST.__name__)

    # Fit exponential distribution
    loc, scale = expon.fit(a)
    λ = 1 / scale
    rv = expon(loc=loc, scale=scale)
    x = np.linspace(a.min(), a.max())
    ax.plot(x, rv.pdf(x), color=c,
            label=f"{λ = :.2f}\n{1 + 1/λ = :.2f} (= mean = std)")

ax.annotate(r"$\lambda e^{-\lambda (x - 1)}$",
            xy=(rv.mean()+0.1, rv.pdf(0.1+rv.mean())), xycoords='data',
            xytext=(5+rv.mean(), rv.pdf(0.1+rv.mean())), textcoords='data',
            ha='center', fontsize=12,
            arrowprops=dict(arrowstyle="->")
            )

ax.set_xlabel(rf"cluster length ({fc.t.N:,d} keys, $M$ = {fc.t.M})", color='C3')
ax.set_ylabel('frequency', color='C3', labelpad=-15)
ax.set_ylim(top=1.1*freqs.max())
ax.set_yticks((0, round(1.1*freqs.max(), 1)))

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.legend()
ax.grid(False)

plt.show()
# =============================================================================
# =============================================================================
