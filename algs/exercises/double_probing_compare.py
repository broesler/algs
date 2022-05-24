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
# from scipy.stats import poisson

from algs.search import SeparateChainingHashST, DoubleProbingHashST
from frequency_counter import FrequencyCounter

MINLEN = 1  # 1, 8, 10
filename = Path('../data/tale.txt')  # 779K


def P(k, μ):
    """Poisson distribution function for any real value `k >= 0`."""
    return μ**k * np.exp(-μ) / factorial(k)
    # NOTE the true PMF is only valid for integer values of `k`
    # return poisson(mu=μ).pmf(k)


# Opts for each table
opts = list([dict({'st': SeparateChainingHashST,
                   'c': 'k',
                   'adj': 0.8}),
             dict({'st': DoubleProbingHashST,
                   'c': 'C3',
                   'adj': 1.2})
             ])

fig = plt.figure(0, clear=True, constrained_layout=True)
fig.set_size_inches((8, 4), forward=True)
ax = fig.add_subplot()

for opt in opts:
    # Add each of the unique words in Tale of Two Cities to the hash table.
    fc = FrequencyCounter(opt['st'], M=997, resize=False)
    fc.count_frequencies(filename, MINLEN)
    a = np.r_[fc.t._list_lengths()]  # empirical list lengths
    σ = a.var()**0.5

    # Plot the histogram of list lengths
    bins = np.arange(25)+0.5
    freqs, _, _ = ax.hist(a, bins=bins, density=True, rwidth=0.9,
                          color=opt['c'], alpha=0.7, label=opt['st'].__name__)

    # Fit Poisson distribution
    μ = a.mean()  # actual mean list length
    x = np.linspace(0, 25)
    Pk = P(x, μ)
    ax.plot(x, Pk, color=opt['c'], label=f"{μ = :.2f}")

    # Plot mean of the list lengths
    ax.axvline(μ, c=opt['c'], lw=1)

    # Annotate the variance
    ax.annotate(f"  {σ = :.2f}",
                xy=(μ - σ, opt['adj']*Pk.max()), xycoords='data',
                xytext=(μ + σ, opt['adj']*Pk.max()), textcoords='data',
                va='center', color=opt['c'],
                arrowprops=dict(arrowstyle="<->", color=opt['c'])
                )


# Expected mean list length
α = fc.t._load_factor
ax.axvline(α, c='k', lw=1)

ax.annotate(f"{α = :.2f}",
            xy=(α, 1.1*freqs.max()), xycoords='data',
            xytext=(α+2, 1.1*freqs.max()), textcoords='data',
            va='center', color='C3',
            arrowprops=dict(arrowstyle='->', color='C3')
            )

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
