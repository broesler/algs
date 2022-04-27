#!/usr/bin/env python3
# =============================================================================
#     File: hash_list_lengths.py
#  Created: 2022-04-26 22:55
#   Author: Bernie Roesler
#
"""
Description: Plot the frequency distribution of list lengths.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import pickle

from pathlib import Path
from scipy.special import factorial

MINLEN = 1  # 1, 8, 10
filename = Path('../data/tale.txt')       # 779K

ST_name = 'SeparateChainingHashST'

tag = filename.stem
kind = 'app'

# Load the FrequencyCounter
with open(f"./pkl/{tag}_{ST_name}_m{MINLEN:02d}_{kind}.pkl", 'rb') as fp:
    fc = pickle.load(fp)

st = fc.t
lens = np.r_[[t.size for t in st._st]]  # empirical list lengths

# Theoretical distribution
α = st.N / st.M                       # mean list length
k = np.linspace(0, 1.5*lens.max())    # number of keys per list

def P(k):
    return α**k * np.exp(-α) / factorial(k)  # Poisson distrbution

Pk = P(k)

# ----------------------------------------------------------------------------- 
#         Plot
# -----------------------------------------------------------------------------
fig = plt.figure(0, clear=True, constrained_layout=True)
fig.set_size_inches((12, 3), forward=True)
ax = fig.add_subplot()
ax.hist(lens, bins=20, density=True, rwidth=0.9, color='k')
ax.plot(k, Pk, 'C3')
ax.axvline(α, c='C3', lw=1)

ax.annotate(f"{α = :.4f}...", xy=(α, 1.1*Pk.max()), xycoords='data', 
            xytext=(α+2, 1.2*Pk.max()), textcoords='data', 
            va='top', ha='left', color='C3',
            arrowprops=dict(arrowstyle='->', color='C3')
            )

ax.annotate(r"$\dfrac{\alpha^k e^{-\alpha}}{k!}$",
            xy=(15, P(15)), xycoords='data', 
            xytext=(18, 0.6*Pk.max()), textcoords='data', 
            va='top', ha='left', color='C3', fontsize=14,
            arrowprops=dict(arrowstyle='->', color='C3')
            )

ax.set_xlabel(rf"list lengths ({st.N:,d} keys, $M$ = {st.M})", 
              fontweight='bold', color='C3')
ax.set_ylabel('frequency',
              fontweight='bold', color='C3', labelpad=-25)
ax.set_yticks([0, 0.125])

ax.spines['top'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.grid(None)

ylim = ax.get_ylim()
ax.set_yticks = ylim
# ax.set_ylim(top=0.18)

plt.show()
# =============================================================================
# =============================================================================
