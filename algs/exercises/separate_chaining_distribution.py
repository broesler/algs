#!/usr/bin/env python3
# =============================================================================
#     File: separate_chaining_distribution.py
#  Created: 2022-04-26 20:51
#   Author: Bernie Roesler
#
"""
Exercise 3.4.36 List length range
Exercise 3.4.38 Insert integers to test Proposition K: The probability that the
number of keys in a list is within a small constant factor of *N/M* is
extremely close to 1.

Assuming uniform hashing (Assumption J), the probability that a given list
will contain *k* keys is a *binomial distribution* with :math:`p = 1/M = α/N`.
For small α, this distribution is approximated by a *Poisson distribution* with
parameter :math:`λ = α`.

The probability that a list has more than `tα` keys is bound by: (1 - CDF(α))

..math::
    (\alpha \frac{e}{t})^t e^{-\alpha}

The average length of the longest list grows with :math:`log N / log log N` for
a given α.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np

from algs.search.hash import SeparateChainingHashST

rng = np.random.default_rng(seed=56)

# Insert N random non-negative integers into a table of size N/100.
Ns = [10**x for x in range(3, 7)]
α = 100  # choose ratio

Ls = dict()
min_Ls = list()
max_Ls = list()

for N in Ns:
    M = N // α
    st = SeparateChainingHashST(M=M, resize=True)
    # TODO run T trials and compute avg length of longest list
    keys = rng.integers(N, size=N)
    # NOTE don't build the entire table for speed. Just hash the values and
    # compute the frequencies of each
    hashes = [st._hash(k) for k in keys]
    counts, bin_edges = np.histogram(hashes, bins=np.arange(M+1))
    Ls[N] = counts
    min_Ls.append(counts.min())
    max_Ls.append(counts.max())

n = np.logspace(2, 7.1)
avg_longest = np.log(n) / np.log(np.log(n))

fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()
ax.plot(n, avg_longest)
ax.scatter(Ns, max_Ls)
ax.set(xlabel='N',
       ylabel='Longest List')

plt.show()

# =============================================================================
# =============================================================================
