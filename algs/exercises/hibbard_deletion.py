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

# Define constant inputs
FORCE_UPDATE = False

PICKLE_FILE = Path('./pkl/hibbard_delete.pkl')
# PICKLE_FILE = Path('./pkl/hibbard_delete_tiny.pkl')

# Input variables
N_TRIALS = 30  # run the entire experiment and ensemble average
dms = ['Hibbard', 'random']  # delete methods
Ns = [2**x for x in range(6, 12)]  # [64, 128, 256, 512, 1024, 2048]
# Ns = [64, 128]

# Output variables
if FORCE_UPDATE or not PICKLE_FILE.exists():
    # Store the ipls vs operations
    ipls = dict()
    for N in Ns:
        print(f"---------- {N} keys...")
        M = int(2*N*N)
        for dm in dms:
            print(f"{dm} deletion...")
            # Re-seed the rng for each variable to compare
            rng = np.random.default_rng(seed=565656)
            avg_ipl = np.empty((N_TRIALS, M))  # track IPL vs. operations

            for trial in tqdm(range(N_TRIALS), desc='trials'):
                # Generate random numbers
                rand_keys = N*rng.random(size=N)        # random \in [0, N)
                rand_deletes = rng.integers(N, size=M)  # select keys uniformly
                rand_inserts = N*rng.random(size=M)

                # Create a symbol table with N keys
                st = BST.fromkeys(rand_keys, delete_method=dm)
                avg_ipl[trial, 0] = 1 + st.internal_path_length / st.size

                # delete and insert random keys N^2 times.
                for i in tqdm(range(1, M), leave=False):
                    del st[st.select(rand_deletes[i])]
                    st[rand_inserts[i]] = None
                    avg_ipl[trial, i] = 1 + st.internal_path_length / st.size

                assert N == st.size

            # Store the ipls vs operations
            ipls[dm, N] = avg_ipl

    with open(PICKLE_FILE, 'wb') as fp:
        pickle.dump(ipls, fp)

else:
    with open(PICKLE_FILE, 'rb') as fp:
        ipls = pickle.load(fp)


# -----------------------------------------------------------------------------
#         Process data
# -----------------------------------------------------------------------------
def theory_avg_ipl(N):
    """Theoretical average internal path length of a random BST.

    ..note:: See Eppinger 1983 for details.
    """
    return 1.386 * np.log2(N) + 2*np.euler_gamma - 3  # ≅ 1.39 lg N - 1.95


# Create summary DataFrame from the ipl data
df = pd.DataFrame(index=pd.MultiIndex.from_product([dms, Ns]),
                  columns=['samples', 'mean_IPL', 'var_IPL'])
df.index.names = ['dm', 'N']

for N in Ns:
    for dm in dms:
        data = ipls[dm, N] / theory_avg_ipl(N)  # normalize the data
        data = data[:, N**2:]                   # take indices > N**2
        df.loc[dm, N]['samples'] = np.size(data)
        df.loc[dm, N]['mean_IPL'] = np.mean(data)
        df.loc[dm, N]['var_IPL'] = np.var(data)

# df = df.reset_index()
print(df)

# -----------------------------------------------------------------------------
#         Plots
# -----------------------------------------------------------------------------
# TODO fit final lengths to: a * N**0.5 + b

# fig = plt.figure(1, clear=True)
# fig.set_size_inches((6, 8), forward=True)
# ax = fig.add_subplot()
# sns.pointplot(data=df, x='N', y='initial', hue='dm', linestyles='--')
# sns.pointplot(data=df, x='N', y='final', hue='dm')
# ax.set_ylabel('Average Path Length')

fig = plt.figure(2, clear=True)
gs = GridSpec(nrows=len(Ns), ncols=1)

for i, N in enumerate(Ns):
    ax = fig.add_subplot(gs[i])
    ax.axhline(1, color='k', lw=1)

    for c, dm in zip(['C0', 'C3'], dms):
        ensemble_avg = np.mean(ipls[dm, N], axis=0)  # avg over trials
        M = len(ensemble_avg)
        ax.plot(range(M),  ensemble_avg / theory_avg_ipl(N),
                color=c, label=f"{dm}, N = {N}")

    ax.set_xticks([0, M/2, M])
    ax.set_xticklabels(['0', '$N^2$', '$2N^2$'])
    ax.legend(loc='upper left', fontsize=8)
    ax.set(xlabel='Operations',
           ylabel='IPL vs. Theory')

# TODO annotate curves with value of N

gs.tight_layout(fig)

plt.show()

# =============================================================================
# =============================================================================
