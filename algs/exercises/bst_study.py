#!/usr/bin/env python3
# =============================================================================
#     File: bst_study.py
#  Created: 2021-02-22 15:13
#   Author: Bernie Roesler
#
r"""
  Description: Ex 3.2.39 and 3.2.40. Tests of number of compares for search
    hits and search misses in a BST, as compared to the theoretical value::

        2 log N + 2 \gamma = 3 \approx 1.39 log N - 1.85

    where $\gamma = 0.57721...$ is *Euler's constant*.

    Estimates the average BST height for multiple values of N, as compared to
    the theoretical value::

        2.99 log N.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib.gridspec import GridSpec
from tqdm import tqdm

from algs.search import BST_nr


def bst_avg_compares(N):
    """Theoretical value of average number of compares in a BST.
    
    From theory, the value is given by::

        2 log N + 2 \gamma - 3 \approx 1.39 log N - 1.85

    where $\gamma = 0.57721...$ is *Euler's constant*.

    Parameters
    ----------
    N : int
        Number of items in the BST.

    Returns
    -------
    result : float
        Expected average number of compares per search in a BST of size `N`.
    """
    return 2*np.log(N) + 2*np.euler_gamma - 3


def bst_height(N):
    """Theoretical height of BST of size `N`."""
    return 2.99 * np.log(N)


# Seed the rng for consistency
rng = np.random.default_rng(seed=565656)

N_trials = 100
# Ns = [int(x) for x in [1e4, 1e5, 1e6]]
# Ns = [int(x) for x in [1e2, 1e3, 1e4]]
Ns = [int(x) for x in [1e3, 1e4, 1e5]]

# Insert N random (with replacement) keys into an initially empty tree
cols = pd.MultiIndex.from_product([
        ['compares', 'height'],
        ['Experiment', 'Theory'],
        ['Avg', 'Std'],
    ])
df = pd.DataFrame(index=Ns, columns=cols)

# Run the experiments
comps = np.empty(N_trials)      # total number of compares to build table
heights = np.empty(N_trials)    # height of tree after building
for N in Ns:
    for i in tqdm(range(N_trials)):
        st = BST_nr()
        tot_comp = 0
        # for k in tqdm(rng.integers(N, size=N)):
        for k in rng.integers(N, size=N):
            st[k] = 1  # set a arbitrary value
            tot_comp += st._cost
        comps[i] = tot_comp / N  # cost of building table of size N
        heights[i] = st.height   # 

    df.loc[N, ('compares', 'Experiment')] = comps.mean(), comps.std()
    df.loc[N, ('compares', 'Theory')]     = bst_avg_compares(N), None
    df.loc[N, ('height', 'Experiment')]   = heights.mean(), heights.std()
    df.loc[N, ('height', 'Theory')]       = bst_height(N), None

# df.to_pickle
print(df)

# =============================================================================
# =============================================================================
