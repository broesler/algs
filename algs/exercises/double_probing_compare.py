#!/usr/bin/env python3
# =============================================================================
#     File: double_probing_compare.py
#  Created: 2022-05-23 17:55
#   Author: Bernie Roesler
#
"""
Plot the frequency distribution of list lengths to compare single probing with
separate chaining to double probing.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path
from scipy.special import factorial
from scipy.stats import binom, poisson, chi2, chisquare

from algs.search import SeparateChainingHashST, DoubleProbingHashST
from frequency_counter import FrequencyCounter

MINLEN = 8  # 1, 8, 10
filename = Path('../data/tale.txt')  # 779K

# -----------------------------------------------------------------------------
#         Plot
# -----------------------------------------------------------------------------
fig = plt.figure(0, clear=True, constrained_layout=True)
fig.set_size_inches((8, 4), forward=True)
ax = fig.add_subplot()

# Plot the histogram of list lengths
for ST, c in zip([SeparateChainingHashST, DoubleProbingHashST], ['k', 'C3']):
    # Add each of the unique words in Tale of Two Cities to the hash table.
    fc = FrequencyCounter(ST, M=997, resize=False)
    fc.count_frequencies(filename, MINLEN)
    α = fc.t._load_factor
    Ls = fc.t._list_lengths()  # empirical list lengths

    ax.hist(Ls, bins=np.arange(23)+0.5, 
            density=True, rwidth=0.9, color=c, alpha=0.8, 
            label=ST.__name__)

    # TODO fit Poisson distribution and compare parameters

ax.axvline(α, c='k', lw=1)

ax.set_xlabel(rf"list length ({fc.t.N:,d} keys, $M$ = {fc.t.M})", color='C3')
ax.set_ylabel('frequency', color='C3', labelpad=-15)
ax.set_yticks([0, max(ax.get_yticks())])

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.legend()
ax.grid(False)

plt.show()
# =============================================================================
# =============================================================================
