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


def count_duplicates(x):
    """Count the number of duplicate entries in a sorted array."""
    x = np.sort(np.asarray(x))
    dups = 0
    for i in range(len(x)-1):
        if x[i+1] == x[i]:
            dups += 1
    return dups


def count_distinct(x):
    """Count the number of distinct entries in a sorted array."""
    x = np.sort(np.asarray(x))
    res = 1
    for i in range(len(x)-1):
        if x[i+1] != x[i]:
            res += 1
    return res


if __name__ == '__main__':
    rng = np.random.default_rng(seed=56)

    T = 10                                    # trials
    Ns = np.r_[[10**e for e in range(3, 6)]]  # number of integers
    alphas = np.r_[2.0, 1.0, 0.5]             # fractions of N

    cols = pd.MultiIndex.from_product((Ns, alphas,
                                    ['duplicate', 'distinct'],
                                    ['actual', 'expect']))
    cols.names = ['N', 'α', '', '']
    data = np.zeros((T, len(cols)), dtype=int)
    df = pd.DataFrame(index=range(T), columns=cols, data=data)
    df.index.name ='T'

    for N in Ns:
        for α in alphas:
            M = N / α   # number of integers
            ints = rng.integers(M, size=(T, N))
            ints = np.sort(ints, axis=1)
            for t in range(T):
                df.loc[t, (N, α, 'duplicate', 'actual')] = count_duplicates(ints[t])
                df.loc[t, (N, α, 'distinct', 'actual')] = count_distinct(ints[t])

    # Average over the trials
    df = (df.mean()
            .unstack([-2, -1])  # move duplicate/distinct, actual/expect to cols
            .reset_index()      # move N, α to cols for math ops
        )

    # Compute expected values
    M = df['N'] // df['α']
    df[('distinct', 'expect')] = M * (1 - np.exp(-df['α']))  # probability theory
    df[('duplicate', 'expect')] = df['N'] - df[('distinct', 'expect')]
    assert np.allclose((df['distinct'] + df['duplicate']).values.T - df['N'].values, 0)

    # Clean-up for presentation
    df = df.set_index(['N', 'α']).round().astype(int)

    print(df)

# =============================================================================
# =============================================================================
