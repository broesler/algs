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

import numpy as np
import pandas as pd
import time

# NOTE our implementations show a similar ratio to np.sort() vs set(), but both
# pale in comparison to the built-in python functions.
# from algs.sort import qsort
# from algs.search import HashSet

def count_both_sort(x):
    """Count the number of duplicates and distinct values in a sorted array."""
    # x = np.sort(np.asarray(x))  # ndarray much faster than `sorted`.
    x = sorted(x)
    # x = qsort(x)
    dups = 0
    uniques = 1
    for i in range(len(x)-1):
        if x[i+1] == x[i]:
            dups += 1
        else:
            uniques += 1
    return dups, uniques


# Exercise 3.5.30
def count_both_dict(x):
    """Count the number of duplicates and distinct entries in an array."""
    st = set()
    # st = HashSet()
    dups = 0
    uniques = 0
    for i in x:
        if i in st:
            dups += 1
        else:
            uniques += 1
            st.add(i)
    return dups, uniques


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
    df.index.name = 'T'

    cols = pd.MultiIndex.from_product((Ns, alphas, ['sort', 'dict']))
    cols.names = ['N', 'α', '']
    data = np.zeros((T, len(cols)), dtype=int)
    tf = pd.DataFrame(index=range(T), columns=cols, data=data)
    tf.index.name = 'T'

    for N in Ns:
        for α in alphas:
            M = N / α   # number of integers
            ints = rng.integers(M, size=(T, N))
            # ints = np.sort(ints, axis=1)
            for t in range(T):
                tic = time.perf_counter_ns()
                dups_sort, dist_sort = count_both_sort(ints[t])
                toc = time.perf_counter_ns()
                dt_sort = toc - tic

                # Exercise 3.5.30
                tic = time.perf_counter_ns()
                dups_dict, dist_dict = count_both_dict(ints[t])
                toc = time.perf_counter_ns()
                dt_dict = toc - tic

                assert dups_sort == dups_dict
                assert dist_sort == dist_dict

                df.loc[t, (N, α, 'duplicate', 'actual')] = dups_sort
                df.loc[t, (N, α, 'distinct', 'actual')] = dist_sort
                tf.loc[t, (N, α, 'sort')] = dt_sort
                tf.loc[t, (N, α, 'dict')] = dt_dict

    # Average over the trials
    df = (df.mean()
            .unstack([-2, -1])  # move dup/distinct, actual/expect to cols
            .reset_index()      # move N, α to cols for math ops
          )

    tf = (tf.mean()
            .unstack(-1)
            .reset_index()
            .set_index(['N', 'α'])
          )
    tf['ratio'] = tf['sort'] / tf['dict']

    # Compute expected values
    M = df['N'] // df['α']
    df[('distinct', 'expect')] = M * (1 - np.exp(-df['α']))  # theory
    df[('duplicate', 'expect')] = df['N'] - df[('distinct', 'expect')]
    assert np.allclose((df['distinct'] + df['duplicate']).values.T
                       - df['N'].values, 0)

    # Clean-up for presentation
    df = df.set_index(['N', 'α']).round().astype(int)

    # TODO plot timing on log scale
    print(df)
    print(tf)

# =============================================================================
# =============================================================================
