#!/usr/bin/env python3
# =============================================================================
#     File: self_org_driver.py
#  Created: 2019-11-17 11:28
#   Author: Bernie Roesler
#
"""
    Description: Ex 3.1.33 Driver for self-organizing search.

    Write a driver program for self-organizing search implementations (see
    Exercise 3.1.22) that uses `get()` to fill a symbol table with N keys, then
    does 10 N successful searches according to a predefined probability
    distribution. Use this driver to compare the running time of your
    implementation from Exercise 3.1.22 with BinarySearchST for N = 1e3, 1e4,
    1e5, and 1e6 using the probability distribution where search hits the ith
    smallest key with probability 1/2^i.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import time

from matplotlib.gridspec import GridSpec

from algs.search import SequentialSearchST, BinarySearchST

Ns = [int(x) for x in [10, 1e2, 1e3]]

runtimes = dict()

for N in Ns:
    print(f"Testing with {N} keys...")
    t = SequentialSearchST(cache=True)
    st = BinarySearchST()  # no caching

    # Fill symbol table with N keys
    keys = np.arange(N)
    for k in keys:
        t[k] = None
        st[k] = None

    M = 10*N

    # Perform 10N successful searches
    # runtimes['SequentialSearchST'] = dict(times=np.array((M,1)), mean=0)

    for i in range(M):
        k = 0 # select key with P(1/2**i)

        # SequentialSearchST
        tic = time.time()
        x = t[k]  # perform get operation
        toc = time.time()
        runtimes['SequentialSearchST'] = tic - toc

        # BinarySearchST
        tic = time.time()
        x = t[k]  # perform get operation
        toc = time.time()
        runtimes['BinarySearchST'] = tic - toc

    # Calcualte average runtime
# ----------------------------------------------------------------------------- 
#         Plots
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True)
ax = fig.add_subplot()
ax.plot(Ns, runtimes['SequentialSearchST'], label='SequentialSearchST')
ax.plot(Ns, runtimes['BinarySearchST'], label='BinarySearchST')
ax.set(xlabel='N',
       ylabel='Runtime [s]')

# =============================================================================
# =============================================================================
