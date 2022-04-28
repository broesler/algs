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

from algs.search.hash import LinearProbingHashST

rng = np.random.default_rng(seed=56)

# Insert N random non-negative integers into a table of size N/100.
Ms = [10**x for x in range(1, 7)]
costs = list()

for M in Ms:
    # TODO run T trials and compute avg
    N = M // 2
    keys = rng.integers(N, size=N)
    st = LinearProbingHashST(M=M).from_keys(keys)
    costs.append(st.cost_of_miss())

costs = np.r_[costs]

α = 1 / 2
th = 1/2 * (1 + 1/(1 - α)**2)

# fig = plt.figure(1, clear=True, constrained_layout=True)
# ax = fig.add_subplot()
# ax.plot()
# ax.set(xlabel='N',
#        ylabel='Longest List')
# plt.show()

# =============================================================================
# =============================================================================
