#!/usr/bin/env python3
# =============================================================================
#     File: separate_chaining_distribution.py
#  Created: 2022-04-26 20:51
#   Author: Bernie Roesler
# =============================================================================

r"""Exercise 3.4.36: List length range
Exercise 3.4.38: Insert integers to test Proposition K: The probability that
the number of keys in a list is within a small constant factor of *N/M* is
extremely close to 1.

Assuming uniform hashing (Assumption J), the probability that a given list will
contain *k* keys is a *binomial distribution* with :math:`p = 1/M = α/N`. For
small α, this distribution is approximated by a *Poisson distribution* with
parameter :math:`λ = α`.

The probability that a list has more than `tα` keys is bound by: (1 - CDF(α))

.. math::
    (\alpha \frac{e}{t})^t e^{-\alpha}

The average length of the longest list grows with :math:`log N / log log N` for
a given α.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import poisson

from algs.search.hash import SeparateChainingHashST

rng = np.random.default_rng(seed=56)

# Insert N random non-negative integers into a table of size N/100.
N = int(1e5)
α = 20
M = N // α  # table size

keys = rng.integers(10 * N, size=N)
st = SeparateChainingHashST.fromkeys(keys, M=M, resize=False)

counts = np.r_[st._list_lengths()]

# Poisson distribution with λ = α
λ = counts.sum() / st.M  # effective α == number of unique keys / table size
x = np.arange(counts.min() - 1, counts.max() + 1)
pois_counts = poisson.pmf(x, λ)

# -----------------------------------------------------------------------------
#        Plot
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(num=2, clear=True)

ax.hist(
    counts,
    bins=np.arange(counts.min() - 0.5, counts.max() + 1),
    density=True,
    rwidth=0.9,
    alpha=0.5,
    label='Data',
)

ax.plot(
    x,
    pois_counts,
    marker="o",
    c='tab:blue',
    label=rf"Pois($\lambda = \alpha = {λ:.2f}$)",
)

ax.legend()
ax.set(title='Distribution of List Lengths', xlabel='list length', ylabel='frequency')

plt.show()

# =============================================================================
# =============================================================================
