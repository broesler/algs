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

    ..note:: See Eppinger 1983 for details.
"""
# =============================================================================

import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib.gridspec import GridSpec
from pathlib import Path
from scipy.signal import resample
from scipy.optimize import curve_fit
from tqdm import tqdm

from algs.search import BST


def theory_avg_ipl(N):
    """Theoretical average internal path length of a random BST.

    ..note:: See Eppinger 1983 for details.
    """
    return 1.386 * np.log2(N) + 2*np.euler_gamma - 3  # ≅ 1.39 lg N - 1.95


# Define constant inputs
FORCE_UPDATE = True

# PICKLE_FILE = Path('./pkl/hibbard_delete.pkl')
PICKLE_FILE = Path('./pkl/hibbard_delete_tiny.pkl')

# Input variables
N_TRIALS = 30  # run the entire experiment and ensemble average
dms = ['Hibbard', 'random']  # delete methods
# Ns = [2**x for x in range(6, 12)]  # [64, 128, 256, 512, 1024, 2048]
Ns = [64, 128]

# Output variables
if FORCE_UPDATE or not PICKLE_FILE.exists():
    # Create summary DataFrame from the ipl data
    df = pd.DataFrame(index=pd.MultiIndex.from_product([dms, Ns]),
                    columns=['samples', 'mean_IPL', 'var_IPL', 
                             'mean_IPL_norm', 'var_IPL_norm'])
    df.index.names = ['dm', 'N']

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

            # Process the stats of the data for summarization
            data = avg_ipl[:, N*N:]
            df.loc[dm, N]['samples'] = np.size(data)
            df.loc[dm, N]['mean_IPL'] = np.mean(data)
            df.loc[dm, N]['var_IPL'] = np.var(data)
            df.loc[dm, N]['mean_IPL_norm'] = np.mean(data / theory_avg_ipl(N))
            df.loc[dm, N]['var_IPL_norm'] = np.var(data / theory_avg_ipl(N))

            # Store downsampled ipls vs operations
            ipls[dm, N] = resample(avg_ipl, num=min(Ns)**2, axis=1)

    with open(PICKLE_FILE, 'wb') as fp:
        pickle.dump((df, ipls), fp)

else:
    with open(PICKLE_FILE, 'rb') as fp:
        df, ipls = pickle.load(fp)

# ----------------------------------------------------------------------------- 
#         Process the data
# -----------------------------------------------------------------------------
print(df)


def func(x, a, b):
    return a * x**0.5 + b


popt, pcov = curve_fit(func, df.xs('Hibbard').index, df.xs('Hibbard')['mean_IPL'])

df = df.reset_index()
df['sqrtN'] = np.sqrt(df['N'])

# -----------------------------------------------------------------------------
#         Plots
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True)
ax = fig.add_subplot()
sns.pointplot(ax=ax, data=df, x='N', y='mean_IPL', hue='dm')
sns.pointplot(ax=ax, data=df, x='N', y='sqrtN', color='k')
ax.set_ylabel('Average Path Length')

ENSEMBLE = True

fig = plt.figure(2, clear=True)
fig.suptitle(f"Ensemble Average Over {N_TRIALS} Trials")
gs = GridSpec(nrows=len(Ns), ncols=1)

for i, N in enumerate(Ns):
    ax = fig.add_subplot(gs[i])
    ax.axhline(1, color='k', lw=1)

    for c, dm in zip(['C0', 'C3'], dms):
        if ENSEMBLE:
            ensemble_avg = np.mean(ipls[dm, N], axis=0)  # avg over trials
            M = len(ensemble_avg)
            ax.plot(range(M),  ensemble_avg / theory_avg_ipl(N),
                    color=c, label=f"{dm}")
        else:
            # Plot all trials separately
            for t in range(N_TRIALS):
                M = ipls[dm, N].shape[1]
                ax.plot(range(M),  ipls[dm, N][t, :] / theory_avg_ipl(N),
                    color=c, label=f"{dm}, N = {N}")

        ax.annotate(rf"$N$ = {N}",
                    xy=(0.01, 0.97), xycoords='axes fraction',
                    ha='left', va='top', color='k')

    # Set ticks but turn labels off for all but last
    ax.set_xticks([0, M/2, M])
    ax.set_xticklabels([])

ax.set_xticklabels(['0', '$N^2$', '$2N^2$'])
ax.legend(fontsize=8)
ax.set(xlabel='Operations',
       ylabel='IPL vs. Theory')

gs.tight_layout(fig)

plt.show()

# =============================================================================
# =============================================================================
