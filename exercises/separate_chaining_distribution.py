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
from tqdm import tqdm

from algs.search.hash import SeparateChainingHashST

rng = np.random.default_rng(seed=56)

# Insert N random non-negative integers into a table of size N/100.
Ns = [10**x for x in range(3, 7)]
α = 100  # choose ratio

Ls = {}
min_Ls = []
max_Ls = []

for N in tqdm(Ns):
    # TODO run T trials and compute avg length of longest list
    M = N // α
    keys = rng.integers(N * N, size=N)
    st = SeparateChainingHashST.fromkeys(keys, M=M, resize=False)
    counts = np.r_[st._list_lengths()]
    Ls[N] = counts
    min_Ls.append(counts.min())
    max_Ls.append(counts.max())

min_Ls = np.r_[min_Ls]
max_Ls = np.r_[max_Ls]

n = np.logspace(2, 7.1)
avg_longest = np.log(n) / np.log(np.log(n))

fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()
ax.plot(n, avg_longest)
ax.scatter(Ns, max_Ls)
ax.set(xlabel='N', ylabel='Longest List')

fig = plt.figure(2, clear=True, constrained_layout=True)
ax = fig.add_subplot()
ax.hist(
    counts,
    bins=np.arange(counts.min() - 0.5, counts.max() + 1),
    density=True,
    rwidth=0.9,
)
ax.set(xlabel='list length', ylabel='frequency')

plt.show()

# =============================================================================
# =============================================================================
