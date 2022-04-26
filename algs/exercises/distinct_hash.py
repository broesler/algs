#!/usr/bin/env python3
# =============================================================================
#     File: distinct_hash.py
#  Created: 2022-04-25 23:57
#   Author: Bernie Roesler
#
"""
  Description:
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from duplicates import count_distinct
from algs.search.hash import SeparateChainingHashST

rng = np.random.default_rng(seed=56)

# Distinct: M*P
# Duplicates: N - M*P
# Free: M - M*P == M*(1 - P)

M = 97  # choose a prime
st = SeparateChainingHashST(M=M)

Ns = np.r_[[10**e for e in range(0, 7)]]
ds = np.zeros(len(Ns))
for i, n in enumerate(Ns):
    keys = rng.random(size=n)  # floats
    ints = np.r_[[st._hash(k) for k in keys]]
    ds[i] = count_distinct(ints)

free_slots = M - ds
df = (pd.DataFrame(data=np.c_[Ns/M, free_slots],
                   index=Ns,
                   columns=['α', 'free'])
        .astype({'free': int})
      )
df['α'] = df['α'].map("{:.2g}".format) 
print(f"{M = }:")
print(df)

# ----------------------------------------------------------------------------- 
#         Plots
# -----------------------------------------------------------------------------
N = np.linspace(0, 5*M)
α = N / M
P = (1 - np.exp(-α))

fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()
# Asymptotes
ax.plot(α, α - 1, 'k--', lw=1)
ax.axhline(1, c='k', ls='--', lw=1)
# Exponentials
ax.plot(α, P, label=r'Distinct = $M(1 - e^{-\alpha})$')
ax.plot(α, α - P, label=r'Duplicate = $N - M(1 - e^{-\alpha})$')
ax.plot(α, 1 - P, label=r'Free Slots = $Me^{-\alpha}$')
ax.set(xlabel=r'$\alpha = \dfrac{N}{M}$',
       ylabel='Fraction of (Distinct/Duplicate) vs. M slots')
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
ax.legend()

plt.show()

# =============================================================================
# =============================================================================
