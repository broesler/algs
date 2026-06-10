#!/usr/bin/env python3
# =============================================================================
#     File: linear_probing_distribution.py
#  Created: 2022-04-28 01:30
#   Author: Bernie Roesler
# =============================================================================

"""Exercise 3.4.39: Insert integers to test Proposition M for LinearProbingHashST."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import expon

from algs.search.hash import LinearProbingHashST

rng = np.random.default_rng(seed=56)

# Insert N random non-negative integers into a table of size N/100.
Ms = np.array([10**x for x in range(3, 8)])
data = []

for M in Ms:
    N = M // 2
    keys = rng.integers(N, size=N)
    st = LinearProbingHashST.fromkeys(keys, M=M, resize=False)
    clusters = np.array(st._cluster_lengths())
    data.append(
        {
            'M': M,
            'N': N,
            'hit': st.cost_of_hit(),
            'miss': st.cost_of_miss(),
            'longest cluster': clusters.max(),
            'mean cluster': clusters.mean(),
        }
    )

df = pd.DataFrame(data)
clusters = np.r_[st._cluster_lengths()]

α = N / M  # == 0.5 by choice of N = M // 2
hit_theory = 0.5 * (1 + 1 / (1 - α))
miss_theory = 0.5 * (1 + 1 / (1 - α) ** 2)

# Fit an exponential distribution to the cluster lengths
# <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.expon.html>
loc, scale = expon.fit(clusters)
λ = 1 / scale
rv = expon(loc=loc, scale=scale)
x = np.linspace(clusters.min(), clusters.max() + 1)

assert np.isclose(clusters.mean(), loc + scale)  # definition of X ~ Exp(λ)

bins = np.arange(clusters.max() + 1) + 0.5

# -----------------------------------------------------------------------------
#        Plots
# -----------------------------------------------------------------------------
# ---------- Cost of Miss vs. N
fig, ax = plt.subplots(num=1, clear=True)

sns.pointplot(
    data=df,
    x='M',
    y='miss',
    native_scale=True,
    ax=ax,
)

ax.axhline(hit_theory, ls='-.', c="tab:blue")
ax.set(ylabel='cost of miss [# probes]', xscale='log')

# ---------- Distribution of cluster lengths
fig, ax = plt.subplots(num=2, clear=True)
fig.set_size_inches((8, 3), forward=True)

ax.hist(clusters, bins=bins, color='k', rwidth=0.9, density=True)
ax.plot(x, rv.pdf(x), c='tab:red', label=rf"${λ:.2f}e^{{{λ:.2f}(x - {loc:.0f})}}$")

ax.set(
    xticks=bins + 0.5,
    xlabel=rf"Cluster Length ($M=${M:,d}, $\alpha = {α:.1f}$)",
    ylabel='Frequency',
    yscale='log',
)
ax.legend()
ax.spines[['top', 'right']].set_visible(False)

plt.show()

# =============================================================================
# =============================================================================
