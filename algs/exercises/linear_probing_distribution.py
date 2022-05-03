#!/usr/bin/env python3
# =============================================================================
#     File: linear_probing_distribution.py
#  Created: 2022-04-28 01:30
#   Author: Bernie Roesler
#
"""
Exercise 3.4.39 Insert integers to test Proposition M for LinearProbingHashST.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np

from scipy.stats import expon

from algs.search.hash import LinearProbingHashST

rng = np.random.default_rng(seed=56)

# TODO 
#   * look at longest cluster length vs. N

# Insert N random non-negative integers into a table of size N/100.
Ms = [10**x for x in range(1, 6)]
costs = list()

for M in Ms:
    N = M // 2
    keys = rng.integers(N, size=N)
    st = LinearProbingHashST(M=M, resize=False).fromkeys(keys)
    costs.append(st.cost_of_miss())

costs = np.r_[costs]

# Discussion: costs are marginally lower for actual vs. theory, but approach
# the theoretical value as N increases.
# [5]>>> list(zip(Ms, costs))
# [5]===
# [(   10, 1.375),
# (   100, 1.828125),
# (  1000, 2.1669921875),
# ( 10000, 2.0484619140625),
# (100000, 2.2954559326171875)]



α = N / M
th_hit = 1/2 * (1 + 1/(1 - α))
th_miss = 1/2 * (1 + 1/(1 - α)**2)

# Fit an exponential distribution to the cluster lengths
a = st._cluster_lengths()
p = expon.fit(a)
rv = expon(loc=p[0], scale=p[1])
x = np.linspace(rv.ppf(0.0001), rv.ppf(0.9999))
bins = np.r_[0, np.arange(a.max()+1)+0.5]

fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()
ax.hist(a, bins=bins, color='k', rwidth=0.8, density=True)
ax.plot(x, rv.pdf(x), 'C3-', label=rf"${p[0]:.1f}e^{{{p[1]:.2f}x}}$")

ax.set(xticks=bins[1:]+0.5,
       xlabel=rf"Cluster Length ($M=${M:,d}, $\alpha = {α:.1f}$)",
       ylabel='Frequency')
ax.legend()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.show()

# =============================================================================
# =============================================================================
