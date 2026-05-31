#!/usr/bin/env python3
# =============================================================================
#     File: erdos_renyi_model.py
#  Created: 2022-05-26 20:50
#   Author: Bernie Roesler
# =============================================================================

"""Exercise 1.5.17: Erdös-Renyi model of random connections."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

from algs.unionfind import ErdosRenyi

FORCE_UPDATE = False
PKL_PATH = Path(__file__).parent / 'pkl'
parquet_file = PKL_PATH / 'erdos_renyi.parquet'

T = 10  # trials

if not FORCE_UPDATE and parquet_file.exists():
    df = pd.read_parquet(parquet_file)
else:
    Ns = [100 * (2**i) for i in range(13)]

    data = []

    for N in tqdm(Ns):
        Es = np.zeros(T)
        for i in tqdm(range(T), leave=False):
            uf = ErdosRenyi(N)
            Es[i] = uf.E

        data.append({'N': N, 'mean': Es.mean(), 'std': Es.std()})

    df = pd.DataFrame(data).set_index('N')
    df['theory'] = 1 / 2 * df.index * np.log(df.index)
    df.to_parquet(parquet_file)

# -----------------------------------------------------------------------------
#         Plot
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()
ax.plot(df.index, df['theory'], c='k', label=r'$\frac{1}{2} N \log N$')
ax.scatter(df.index, df['mean'], c='C3', label=f"data ({T=} trials)")
ax.set(xlabel='N', xscale='log', ylabel='# edges', yscale='log')
ax.legend()

plt.show()
# =============================================================================
# =============================================================================
