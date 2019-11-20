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

import pickle
import time

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

from tqdm import tqdm
from matplotlib.gridspec import GridSpec

from algs.search import SequentialSearchST, BinarySearchST

zipf = False

def H_N(N):
    """Harmonic number `N`."""
    return np.array([np.sum([1.0 / i  for i in np.arange(1, n)]) 
                     for n in np.asarray(N)])

# Define sequence of N to test
Ns = [int(x) for x in [10, 1e2, 1e3, 2e3, 5e3, 1e4, 2e4]]
names = [x.__name__ for x in [SequentialSearchST, BinarySearchST]]
Ns_str = [str(x) for x in Ns]

N_s = 100  # number of search times to sample

# Store the runtimes
cols = pd.MultiIndex.from_product([names, Ns_str], names=['ST', 'N'])
data = np.empty((N_s, len(names)*len(Ns_str)))
df = pd.DataFrame(columns=cols, data=data)

for N in Ns:
    M = 10*N

    for t in [SequentialSearchST(cache=True), BinarySearchST()]:
        print(f"Testing with {N} keys...")

        # Fill symbol table with N keys
        # TODO time puts() as well as gets() ['put', 'get']
        keys = np.arange(N)
        np.random.shuffle(keys)  # random insertion order
        for k in keys:
            t[k] = None
        keys.sort()

        # Pre-determined probability of searching for key `i`
        if zipf:
            probs = 1 / ((keys+1.0) * H_N(keys))
        else:
            probs = 1 / (2.0**(keys + 1.0))

        probs /= np.sum(probs)  # normalize to 1

        # Perform 10N successful searches
        runtimes = np.empty(M)
        # for i in range(M):
        for i in tqdm(range(M), total=M):
            k = np.random.choice(keys, p=probs)

            tic = time.time()
            x = t[k]  # perform get operation
            toc = time.time()

            runtimes[i] = toc - tic

        # Randomly sample the search times for easier plotting
        idx = np.random.randint(0, M, size=N_s)
        df[(t.__class__.__name__, str(N))] = runtimes[idx]

# pickle.dump(df, open('runtimes.pkl', 'wb'))
df = pickle.load(open('runtimes.pkl', 'rb'))

# ----------------------------------------------------------------------------- 
#         Plots
# -----------------------------------------------------------------------------
tf = df.melt(value_name='runtime')  # prep for plotting

# Plot distributions of runtimes
fig = plt.figure(1, clear=True)
ax = fig.add_subplot()

# Plot the runtime distributions
sns.stripplot(data=tf, x='N', y='runtime', hue='ST',
              dodge=True, jitter=True, alpha=0.25, zorder=1)

# PLot the means of each group
# sns.pointplot(data=tf, x='N', y='runtime', hue='ST',
#               dodge=0.4, join=False, markers='d',
#               palette='dark')

# Nice legend
h, l = ax.get_legend_handles_labels()
ax.legend(h[2:], l[2:], title='Symbol Table',
          handletextpad=0, labelspacing=1,
          loc='upper left', frameon=True)

ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
ax.set_ylim([0.9*tf['runtime'].min(), 1.1*tf['runtime'].max()])
ax.set_ylabel('time per search [s]')

# Plot total runtimes
fig = plt.figure(2, clear=True)
ax = fig.add_subplot()
ax.plot(Ns, 10*N_s*1000*df['SequentialSearchST'].mean(), 'x-', label='SequentialSearchST')
ax.plot(Ns, 10*N_s*1000*df['BinarySearchST'].mean(),     'x-', label='BinarySearchST')
ax.set(xlabel='N',
       ylabel='Runtime [s]')
ax.legend()

plt.show()
# =============================================================================
# =============================================================================
