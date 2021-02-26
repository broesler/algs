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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib.gridspec import GridSpec
from pathlib import Path
from tqdm import tqdm

from algs.search import BST

FORCE_UPDATE = True
PICKLE_FILE = Path('./pkl/hibbard_delete.pkl')

rng = np.random.default_rng(seed=565656)

# Input variables
dms = ['Hibbard', 'random']  # delete methods

# Ns = [int(n) for n in np.logspace(2, 4)]
Ns = [100, 1000, 10_000]

# Output variables
if FORCE_UPDATE or not PICKLE_FILE.exists():
    df = pd.DataFrame(index=pd.MultiIndex.from_product([dms, Ns]),
                    columns=['initial', 'final'])
    df.index.names = ['dm', 'N']

    for dm in dms:
        print(f"---------- {dm} deletion...")
        for N in Ns:
            print(f"{N} keys...")
            # Create a symbol table with N keys
            st = BST(delete_method=dm)\
                    .fromkeys(rng.choice(N, size=N, replace=False))
            df.loc[dm, N]['initial'] = 1 + st.internal_path_length / N
            # delete and re-insert random keys N^2 times.
            M = int(N*N)
            for k in tqdm(rng.integers(N, size=M)):
                del st[k]
                st[k] = None
            assert st.size == N
            df.loc[dm, N]['final'] = 1 + st.internal_path_length / N

    with open(PICKLE_FILE, 'wb') as fp:
        df.to_pickle(fp)
                
else:
    with open(PICKLE_FILE, 'rb') as fp:
        df = pd.read_pickle(fp)

df = df.reset_index()

# ----------------------------------------------------------------------------- 
#         Plots
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True)
ax = fig.add_subplot()
sns.pointplot(data=df, x='N', y='initial', hue='dm', linestyles='--')
sns.pointplot(data=df, x='N', y='final', hue='dm')
ax.set_ylabel('Average Path Length')

plt.show()

# =============================================================================
# =============================================================================
