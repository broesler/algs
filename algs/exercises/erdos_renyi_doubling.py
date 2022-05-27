#!/usr/bin/env python3
# =============================================================================
#     File: erdos_renyi_doubling.py
#  Created: 2022-05-26 22:12
#   Author: Bernie Roesler
#
"""
Exercise 1.5.22 Doubling test for the Erdös-Renyi model.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time

from pathlib import Path
from tqdm import tqdm

from algs.unionfind import (ErdosRenyi, QuickFindUF, QuickUnionUF,
                            WeightedQuickUnionUF)

FORCE_UPDATE = False
pkl_file = Path('./pkl/erdos_renyi_doubling.pkl')

UFs = [QuickFindUF, QuickUnionUF, WeightedQuickUnionUF]
names = ['quick-find', 'quick-union', 'weighted quick-union']

if not FORCE_UPDATE and pkl_file.exists():
    df = pd.read_pickle(pkl_file)
else:
    T = 10  # trials
    Ns = [250*(2**i) for i in range(7)]

    df = pd.DataFrame(index=Ns, data=np.zeros((len(Ns), 2*len(names))),
                    columns=pd.MultiIndex.from_product([['edges', 'time'], names]))
    df.index.name = 'N'
    df.columns.names = ['var', 'name']

    for N in tqdm(Ns):
        for name, UF in zip(names, UFs):
            edges = np.zeros(T)
            for i in tqdm(range(T), leave=False):
                tic = time.perf_counter()
                uf = ErdosRenyi(N, UF=UF)
                toc = time.perf_counter()
                edges[i] = uf.edges
            df.loc[N, ('edges', name)] = edges.mean()
            df.loc[N, ('time', name)] = toc - tic

    df.to_pickle(pkl_file)

# Compute time ratio
ratios = np.full((df.index.size, len(UFs)), np.nan)
ratios[1:] = df['time'].iloc[1:].values / df['time'].iloc[:-1].values
idx = pd.MultiIndex.from_product([['ratio'], names])
df[idx] = ratios

# Fit power law to the data T(N) ~ a * N**b

# =============================================================================
# =============================================================================
