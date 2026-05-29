#!/usr/bin/env python3
# =============================================================================
#     File: erdos_renyi_doubling.py
#  Created: 2022-05-26 22:12
#   Author: Bernie Roesler
# =============================================================================

"""Exercise 1.5.22 Doubling test for the Erdös-Renyi model."""

import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from tqdm import tqdm

from algs.unionfind import ErdosRenyi, QuickFindUF, QuickUnionUF, WeightedQuickUnionUF

FORCE_UPDATE = False
PKL_PATH = Path(__file__).parent / 'pkl'
pkl_file = PKL_PATH / 'erdos_renyi_doubling.pkl'

UFs = [QuickFindUF, QuickUnionUF, WeightedQuickUnionUF]
names = ['quick-find', 'quick-union', 'weighted quick-union']

if not FORCE_UPDATE and pkl_file.exists():
    df = pd.read_pickle(pkl_file)
else:
    T = 10  # trials
    Ns = [250 * (2**i) for i in range(7)]

    data = []

    for N in tqdm(Ns):
        for name, UF in zip(names, UFs):
            Es = np.zeros(T)
            for i in tqdm(range(T), leave=False):
                tic = time.perf_counter_ns()
                uf = ErdosRenyi(N, UF=UF)
                toc = time.perf_counter_ns()
                Es[i] = uf.E

            data.append({
                'N': N,
                'name': name,
                'edges': Es.mean(),
                'time': toc - tic,
            })

    df = pd.DataFrame(data).pivot_table(
        index='N',
        columns='name',
        values=['edges', 'time'],
    )

    df.to_pickle(pkl_file)

# Compute time ratio
ratios = df['time'] / df['time'].shift(1)
idx = pd.MultiIndex.from_product([['ratio'], ratios.columns])
df[idx] = ratios
print(df['ratio'])


# Fit power law to the data T(N) ~ a * N**b -> log-space
def power_func(N, a, b):
    """Power law function."""
    return a + b * np.log2(N)


tf = df['ratio'].dropna(axis=0)

popt = {}
pcov = {}
for name in names:
    popt[name], pcov[name] = curve_fit(
        power_func,
        np.log2(tf.index.values),
        np.log2(tf[name].values),
    )
print(popt)

x = np.log2(tf.index.values)
A = np.c_[np.ones_like(x), x]  # linear matrix
b = np.log2(tf.values)
theta = np.linalg.lstsq(A, b, rcond=None)
print(theta[0])

# =============================================================================
# =============================================================================
