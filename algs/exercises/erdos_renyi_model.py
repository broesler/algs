#!/usr/bin/env python3
# =============================================================================
#     File: erdos_renyi_model.py
#  Created: 2022-05-26 20:50
#   Author: Bernie Roesler
#
"""
Exercise 1.5.17 Erdös-Renyi model of random connections.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pathlib import Path
from tqdm import tqdm

from algs.unionfind import ErdosRenyi

FORCE_UPDATE = False
pkl_file = Path('./pkl/erdos_renyi.pkl')

T = 10  # trials

if not FORCE_UPDATE and pkl_file.exists():
    df = pd.read_pickle(pkl_file)
else:
    Ns = [100*(2**i) for i in range(13)]

    df = pd.DataFrame(index=Ns, data=np.zeros((len(Ns), 2)),
                    columns=['mean', 'std'])

    for N in tqdm(Ns):
        edges = np.zeros(T)
        for i in tqdm(range(T), leave=False):
            uf = ErdosRenyi(N)
            edges[i] = uf.edges

        df.loc[N, 'mean'] = edges.mean()
        df.loc[N, 'std'] = edges.std()

    df['theory'] = 1/2 * df.index * np.log(df.index)
    df.to_pickle(pkl_file)

# ----------------------------------------------------------------------------- 
#         Plot
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()
ax.plot(df.index, df['theory'], c='k', label=r'$\frac{1}{2} N \log N$')
ax.scatter(df.index, df['mean'], c='C3', label=f"data ({T=} trials)")
ax.set(xlabel='N', xscale='log',
       ylabel='# edges', yscale='log')
ax.legend()

plt.show()
# =============================================================================
# =============================================================================
