#!/usr/bin/env python3
# =============================================================================
#     File: self_org_driver.py
#  Created: 2019-11-17 11:28
#   Author: Bernie Roesler
#
"""
    Description: Plots for Ex 3.1.33 (self-organizing search)
"""
# =============================================================================

import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib.gridspec import GridSpec
from pathlib import Path

filename = Path(f"./pkl/runtimes.pkl")

with open(filename, 'rb') as f:
    df, tots, keys, Ns = pickle.load(f)

ST_names = df.columns.get_level_values('ST').unique()

# ----------------------------------------------------------------------------- 
#         Plots
# -----------------------------------------------------------------------------
tf = df.melt(value_name='runtime')

# Plot distributions of runtimes
fig = plt.figure(1, clear=True)
ax = fig.add_subplot()

# Plot the runtime distributions
sns.stripplot(data=tf, x='N', y='runtime', hue='ST',
              dodge=True, jitter=True, alpha=0.25, zorder=1)

# PLot the means of each group
sns.pointplot(data=tf, x='N', y='runtime', hue='ST',
              dodge=0.5, join=False, markers='d',
              palette='dark')

# Nice legend
h, l = ax.get_legend_handles_labels()
ax.legend(h[3:], l[3:], title='Symbol Table',
          handletextpad=0, labelspacing=1,
          loc='upper left', frameon=True)

ax.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
ax.set(ylim=[0.9*tf['runtime'].min(), 1.1*tf['runtime'].max()],
       ylabel='time per search [s]',
       yscale='log')
ax.grid()
fig.tight_layout()

# Plot total runtimes
fig = plt.figure(2, clear=True)
gs = GridSpec(nrows=1, ncols=2)
for i, dist in enumerate(['p', 'zipf']):
    ax = fig.add_subplot(gs[i])
    for op, m in zip(['put', 'get'], ['x', 'o']):
        for i, name in enumerate(ST_names):
            ax.plot(Ns, tots.xs([dist, name, op], 
                    level=['dist', 'ST', 'op']),
                    c=f"C{i}", marker=m, ls='-',
                    label=f"{name}: {op}")

    ax.set(title='Zipf' if dist == 'zipf' else '$1/2^i$',
           xlabel='N',
           ylabel='Runtime [s]',
           xscale='log',
           yscale='log')
    ax.grid()
    ax.legend()

# Plot keys vs. index
fig = plt.figure(3, clear=True)
ax = fig.add_subplot()
N = 1000
gs = GridSpec(nrows=1, ncols=2)
for i, dist in enumerate(['p', 'zipf']):
    ax = fig.add_subplot(gs[i])
    for name in ST_names:
        ax.scatter(np.arange(N), keys[(dist, name, N)],
                alpha=0.5,
                label=name)
    ax.set(title='Zipf' if dist == 'zipf' else '$1/2^i$',
           xlabel='index',
           ylabel='key')
    ax.legend(loc='lower right')

plt.show()
# =============================================================================
# =============================================================================
