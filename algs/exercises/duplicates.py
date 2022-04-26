#!/usr/bin/env python3
# =============================================================================
#     File: duplicates.py
#  Created: 2022-04-25 19:38
#   Author: Bernie Roesler
#
"""
Solution to Exercise 2.5.31 Duplicates. A client that computes the number of
duplicates in *N* random integers on *[0, M-1]*, for *T* trials. Probability
theory states the number of duplicates should be:

.. math::
    P(\alpha) = 1 - e^{-\alpha}
    D = NP

"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import scipy.linalg as la
import pandas as pd

from algs.sort import is_sorted


def count_duplicates(x):
    """Count the number of duplicate entries in a sorted array."""
    assert is_sorted(x)
    dups = 0
    for i in range(len(x)-1):
        if x[i+1] == x[i]:
            dups += 1
    return dups


def count_distinct(x):
    """Count the number of distinct entries in a sorted array."""
    assert is_sorted(x)
    res = 1
    for i in range(len(x)-1):
        if x[i+1] != x[i]:
            res += 1
    return res


rng = np.random.default_rng(seed=56)

T = 10                                    # trials
Ns = np.r_[[10**e for e in range(3, 6)]]  # number of integers
alphas = np.r_[2.0, 1.0, 0.5]             # fractions of N

cols = pd.MultiIndex.from_product((Ns, alphas, ['dups_a', 'distinct_a']))
cols.names = ['N', 'α', 'kind']
data = np.zeros((T, len(Ns)*len(alphas)*2), dtype=int)
df = pd.DataFrame(index=range(T), columns=cols, data=data)
df.index.name ='T'

for N in Ns:
    for α in alphas:
        M = N / α   # number of integers
        ints = rng.integers(M, size=(T, N))
        ints = np.sort(ints, axis=1)
        for t in range(T):
            df.loc[t, (N, α, 'dups_a')] = count_duplicates(ints[t])
            df.loc[t, (N, α, 'distinct_a')] = count_distinct(ints[t])

# Average over the trials
df = (df.mean()
        .unstack()
        .astype(int)
        .reset_index()
      )
M = (df['N'] / df['α']).astype(int)
df['expect_distinct'] = (M * (1 - np.exp(-df['α']))).astype(int)
df['expect_dups'] = df['N'] - df['distinct_a']
# df['a/e'] = df['actual'] / df['expect']
df = df.set_index(['N', 'α'])
df = df[df.columns[[0, 2, 1, 3]]]  # swap order


# # ----------------------------------------------------------------------------- 
# #         Plots
# # -----------------------------------------------------------------------------
# M = 100
# N = np.linspace(0, 2*M)
# α = N / M
# D = M * (1 - np.exp(-α))

# fig = plt.figure(1, clear=True, constrained_layout=True)
# ax = fig.add_subplot()
# ax.plot(N, D, label=f"Distinct, M = {M}")
# ax.plot(N, N - D, label=f"Duplicate, M = {M}")
# ax.set(xlabel='N',
#        ylabel='Number of Items')

# =============================================================================
# =============================================================================
