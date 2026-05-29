#!/usr/bin/env python3
# =============================================================================
#     File: double_probing_compare.py
#  Created: 2022-05-23 17:55
#   Author: Bernie Roesler
# =============================================================================

"""Plot the frequency distribution of list lengths to compare single probing
with separate chaining to double probing.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from frequency_counter import FrequencyCounter
from scipy.optimize import curve_fit
from scipy.special import loggamma  # , factorial

# from scipy.stats import poisson
from algs.search import DoubleProbingHashST, SeparateChainingHashST

MINLEN = 1  # 1, 8, 10
DATA_PATH = Path(__file__).parent.parent / 'data'
filename = DATA_PATH / 'tale.txt'  # 779K


def P(k, μ, λ=0):
    """General Poisson distribution function for any real value `k >= 0`."""
    # The definition is numerically unstable because λ^k and k! may overflow:
    # return μ**k * np.exp(-μ) / factorial(k)                    # standard
    # return μ*(μ + λ*k)**(k-1) * np.exp(-μ-λ*k) / factorial(k)  # general

    # Use this definition for numerical stability:
    # return np.exp(k*np.log(μ) - μ - loggamma(k + 1))
    return np.exp(np.log(μ) + (k - 1) * np.log(μ + λ * k) - μ - λ * k - loggamma(k + 1))

    # NOTE the true PMF is only valid for integer values of `k`:
    # return poisson(mu=μ).pmf(k)


# Opts for each table
opts = [
    {'st': SeparateChainingHashST, 'c': 'k', 'adj': 0.7},
    {'st': DoubleProbingHashST, 'c': 'C3', 'adj': 0.8},
]

fig = plt.figure(0, clear=True, constrained_layout=True)
fig.set_size_inches((8, 4), forward=True)
ax = fig.add_subplot()

for opt in opts:
    # Add each of the unique words in Tale of Two Cities to the hash table.
    fc = FrequencyCounter(opt['st'], M=997, resize=False)
    fc.count_frequencies(filename, MINLEN)
    a = np.r_[fc.t._list_lengths()]  # empirical list lengths

    # Plot the histogram of list lengths
    bins = np.arange(25) + 0.5
    freqs, _, _ = ax.hist(
        a,
        bins=bins,
        density=True,
        rwidth=0.9,
        color=opt['c'],
        alpha=0.7,
        label=opt['st'].__name__,
    )

    # Fit Poisson distribution
    bin_mids = 0.5 * (bins[1:] + bins[:-1])
    μ, σ = a.mean(), a.var() ** 0.5  # actual data
    (μ_p, λ_p), pcov = curve_fit(P, bin_mids, freqs, p0=(μ, 0))
    x = np.linspace(0, 25)
    Px = P(x, μ_p, λ_p)
    pmu, psig = μ_p / (1 - λ_p), (μ_p / (1 - λ_p) ** 3) ** 0.5
    # fit distribution
    ax.plot(x, Px, color=opt['c'], label=f"GPois(k; μ={μ_p:.2f}, λ={λ_p:.2f})")

    # Annotate the variance
    ax.annotate(
        (
            f"  {μ = :.2f},  $\\mu_p$ = {pmu:.2f}\n"
            rf"  {σ = :.2f},  $\sigma_p$ = {psig:.2f}"
        ),
        xy=(μ - σ, opt['adj'] * np.nanmax(Px)),
        xycoords='data',
        xytext=(μ + σ, opt['adj'] * np.nanmax(Px)),
        textcoords='data',
        va='center',
        color=opt['c'],
        arrowprops={'arrowstyle': "<->", 'color': opt['c']},
    )

# Expected mean list length
α = fc.t._load_factor
ax.axvline(α, c='k', lw=1)

# expected Poisson distribution
ax.plot(x, P(x, α), color='C0', label=f"Pois(k; μ={α=:.2f})")

ax.annotate(
    f"{α = :.2f}",
    xy=(α, 1.1 * freqs.max()),
    xycoords='data',
    xytext=(α + 2, 1.1 * freqs.max()),
    textcoords='data',
    va='center',
    color='C3',
    arrowprops={'arrowstyle': '->', 'color': 'C3'},
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
