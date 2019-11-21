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

import os
import pickle
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib.gridspec import GridSpec
from tqdm import tqdm

from algs.search import SequentialSearchST, BinarySearchST

zipf = False

def H_N(N):
    """Harmonic number `N`."""
    return np.array([1 + np.sum([1.0 / i  for i in np.arange(1, n)]) 
                     for n in np.asarray(N)])

def find_nearest(a, v):
    """Find the value in `a` nearest to `v`."""
    a = np.asarray(a)
    idx = (np.abs(a - v)).argmin()
    return a[idx]

# Define sequence of N to test
Ns = [int(x) for x in [10, 1e2, 1e3, 2e3, 5e3, 1e4]]

N_s = 100  # number of search times to sample

zz = '_zipf' if zipf else ''
filename = f"./pkl/runtimes{zz}.pkl"

if os.path.exists(filename):
    df, tots = pickle.load(open(filename, 'rb'))
else:
    # Store the individual search runtimes
    ST_names = [x.__name__ for x in [SequentialSearchST, BinarySearchST]]

    cols = pd.MultiIndex.from_product([ST_names, ['put', 'get'], Ns],
                                    names=['ST', 'op', 'N'])
    data = np.empty((N_s, len(ST_names)*len(Ns)))

    df = pd.DataFrame(columns=cols.droplevel('op').unique(), data=data)
    tots = pd.Series(index=cols)

    for N in Ns:
        M = 10*N

        for ST in [SequentialSearchST, BinarySearchST]:
            print(f"Filling table with {N} keys...")
            put_tic = time.perf_counter()
            keys = np.arange(N)
            np.random.shuffle(keys)  # random insertion order

            # Fill the symbol table with keys (no values needed)
            t = ST([(k, None) for k in keys], cache=isinstance(ST, SequentialSearchST))

            # Time the insertions separately
            put_toc = time.perf_counter()
            tots[(t.__class__.__name__, 'put', N)] = put_toc - put_tic

            # Pre-determined probability of searching for key `i`
            keys.sort()
            if zipf:
                probs = 1 / ((keys+1.0) * H_N(keys))
            else:
                probs = 1 / (2.0**(keys + 1.0))

            probs /= np.sum(probs)  # normalize to 1

            print(f"Performing 10N successful searches...")
            runtimes = np.empty(M)
            get_tic = time.perf_counter()
            for i in tqdm(range(M), total=M):
                k = np.random.choice(keys, p=probs)

                tic = time.perf_counter()
                x = t[k]  # perform get operation
                toc = time.perf_counter()

                runtimes[i] = toc - tic
            get_toc = time.perf_counter()

            # Randomly sample the search times for easier plotting
            idx = np.random.randint(0, M, size=N_s)
            df[(t.__class__.__name__, N)] = runtimes[idx]
            tots[(t.__class__.__name__, 'get', N)] = get_toc - get_tic

    pickle.dump((df, tots), open(filename, 'wb'))

# ----------------------------------------------------------------------------- 
#         Plots
# -----------------------------------------------------------------------------
tf = df.melt(value_name='runtime')

# Plot distributions of runtimes
fig = plt.figure(1, clear=True)
ax = fig.add_subplot()

# Plot the runtime distributions
sns.stripplot(data=tf, x='N', y='runtime', hue='ST',
              dodge=True, jitter=True, alpha=0.25, zorder=1)

# PLot the means of each group
sns.pointplot(data=tf, x='N', y='runtime', hue='ST',
              dodge=0.4, join=False, markers='d',
              palette='dark')

# Nice legend
h, l = ax.get_legend_handles_labels()
ax.legend(h[2:], l[2:], title='Symbol Table',
          handletextpad=0, labelspacing=1,
          loc='upper left', frameon=True)

ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
ax.set(ylim=[0.9*tf['runtime'].min(), 1.1*tf['runtime'].max()],
       ylabel='time per search [s]',
       yscale='log')

# Plot total runtimes
fignum = 2
for op in ['put', 'get']:
    fig = plt.figure(fignum, clear=True)
    ax = fig.add_subplot()
    ax.plot(Ns, tots.xs(['SequentialSearchST', op], level=['ST', 'op']),
            'x-', label='SequentialSearchST')
    ax.plot(Ns, tots.xs(['BinarySearchST', op], level=['ST', 'op']),
            'x-', label='BinarySearchST')
    ax.set(title=f'`{op}()` operations',
           xlabel='N',
           ylabel='Runtime [s]',
           xscale='log',
           yscale='log')
    ax.legend()
    fignum += 1

plt.show()
# =============================================================================
# =============================================================================
