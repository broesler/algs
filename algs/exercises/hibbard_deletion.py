#!/usr/bin/env python3
# =============================================================================
#     File: hibbard_deletion.py
#  Created: 2021-02-26 14:43
#   Author: Bernie Roesler
#
"""
  Description: Exercise 3.2.42 Hibbard Deletion Degradation
    Write a program that takes an integer N from the command line, builds
    a random BST of size N, then enters into a loop where it deletes a random
    key (using the code `delete(select(StdRandom.uniform(N)))`) and then
    inserts a random key, iterating the loop N^2 times. After the loop, measure
    and print the average length of a path in the tree (the internal path
    length divided by N, plus 1). Run your program for N = 10^2, 10^3, and 10^4
    to test the somewhat counterintuitive hypothesis that this process
    increases the average path length of the tree to be proportional to the
    square root of N. Run the same experiments for a `delete()` implementation
    that makes a random choice whether to use the predecessor or the successor
    node.
"""
# =============================================================================

import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib.gridspec import GridSpec
from pathlib import Path
from tqdm import tqdm

from algs.search import BST

FORCE_UPDATE = False

PICKLE_FILE = Path('./pkl/hibbard_delete.pkl')

rng = np.random.default_rng(seed=565656)

# Input variables
dms = ['Hibbard', 'random']  # delete methods

Ns = [10, 100, 1000]

# Output variables
if FORCE_UPDATE or not PICKLE_FILE.exists():
    df = pd.DataFrame(index=pd.MultiIndex.from_product([dms, Ns]),
                    columns=['initial', 'final', 'sqrt'])
    df.index.names = ['dm', 'N']

    ipls = dict()

    for N in Ns:
        print(f"---------- {N} keys...")
        M = int(N*N)
        rand_keys = N*rng.random(size=N)  # random \in [0, N)
        rand_deletes = rng.integers(N, size=M)  # select keys uniformly
        rand_inserts = N*rng.random(size=M)
        for dm in dms:
            print(f"{dm} deletion...")
            # Create a symbol table with N keys
            st = BST.fromkeys(rand_keys, cache=True, delete_method=dm)
            df.loc[dm, N]['initial'] = 1 + st.internal_path_length / st.size

            # track IPL vs. operations
            avg_ipl = np.empty(M)

            # delete and insert random keys N^2 times.
            for i in tqdm(range(M)):
                del st[st.select(rand_deletes[i])]
                st[rand_inserts[i]] = None
                avg_ipl[i] = 1 + st.internal_path_length / st.size

            assert N == st.size
            ipls[dm, N] = avg_ipl
            df.loc[dm, N]['final'] = 1 + st.internal_path_length / st.size

    with open(PICKLE_FILE, 'wb') as fp:
        pickle.dump((df, ipls), fp)
                
else:
    with open(PICKLE_FILE, 'rb') as fp:
        df, ipls = pickle.load(fp)

df = df.reset_index()

# ----------------------------------------------------------------------------- 
#         Plots
# -----------------------------------------------------------------------------
# TODO fit final lengths to: a * N**0.5 + b
fig = plt.figure(1, clear=True)
ax = fig.add_subplot()
sns.pointplot(data=df, x='N', y='initial', hue='dm', linestyles='--')
sns.pointplot(data=df, x='N', y='final', hue='dm')
ax.set_ylabel('Average Path Length')

fig = plt.figure(2, clear=True)
ax = fig.add_subplot()
for c, dm in zip(['C0', 'C3'], dms):
    for N in Ns:
        M = N*N
        ax.plot(np.linspace(0, 1, num=M), ipls[dm, N], 
                color=c, label=f"{dm}, N = {N}")

# TODO annotate curves with value of N
ax.set_xticks([0, 1])
ax.set_xticklabels(['0', r'$N^2$')
ax.legend(['Hibbard', 'random'])
ax.set(xlabel='Operations',
       ylabel='Average Internal Path Length')

plt.show()

# =============================================================================
# =============================================================================
