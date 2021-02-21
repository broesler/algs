#!/usr/bin/env python3
# =============================================================================
#     File: self_org_plots.py
#  Created: 2019-11-17 11:28
#   Author: Bernie Roesler
#
"""
    Description: Plots for Ex 3.1.33 (self-organizing search)
"""
# =============================================================================

import gzip
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from matplotlib.gridspec import GridSpec
from pathlib import Path

from self_org_driver import SelfOrganizingDriver

SAVE_FIGS = False

if SAVE_FIGS:
    plt.close('all')
    fig_dir = Path('./figures/')

# TODO
#   * add `_randinit` to df, plots as well for comparison
# Load the data
filename = Path('./pkl/self_org_drivers.pkl.gz')

with gzip.open(filename, 'rb') as f:
    drivers = pickle.load(f)

# Reorganize data to plot
dists, ST_names = set(), set()
for k in drivers:
    dists.add(k[0])
    ST_names.add(k[1])

dists, ST_names = sorted(dists), sorted(ST_names)
ops = ['put', 'get']
Ns = np.unique([v.t.size for k, v in drivers.items()])

N_s = drivers[(dists[0], ST_names[0], Ns[0])].runtimes.size

# Store the individual search runtimes
cols = pd.MultiIndex.from_product([dists, ST_names, ops, Ns],
                                names=['dist', 'ST', 'op', 'N'])
data = np.empty((N_s, len(dists)*len(ST_names)*len(Ns)*2))

df = pd.DataFrame(columns=cols.droplevel('op').unique(),
                  data=data[:, :data.shape[1]//len(dists)])
tots = pd.Series(index=cols, name='runtime [s]', dtype=float)

for (d, ST_name, N), driver in drivers.items():
    tots[(d, ST_name, 'put', N)] = driver.put_time
    tots[(d, ST_name, 'get', N)] = driver.get_time
    df[(d, ST_name, N)] = driver.runtimes


# ----------------------------------------------------------------------------- 
#         Plot distributions of runtimes
# -----------------------------------------------------------------------------
tf = df.melt(value_name='runtime')

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

# Tidy up axes limits and labels
ax.ticklabel_format(axis='y', style='sci', scilimits=(-3, 3))
ax.set(ylim=[0.5*tf['runtime'].min(), 5*tf['runtime'].max()],
       ylabel='time per search [s]',
       yscale='log')
ax.grid('on')
fig.tight_layout()

if SAVE_FIGS:
    fig.savefig(fig_dir.joinpath('self_org_timedists.pdf'))

# ----------------------------------------------------------------------------- 
#         Plot total runtimes
# -----------------------------------------------------------------------------
g = sns.FacetGrid(tots.reset_index(), row='op', col='dist', hue='ST',
                  margin_titles=True, height=4)
g.set(xscale='log',
      yscale='log')
g.map(plt.plot, 'N', 'runtime [s]', marker='o')
g.add_legend()
g.tight_layout()

if SAVE_FIGS:
    g.savefig(fig_dir.joinpath('self_org_tots.pdf'))

# ----------------------------------------------------------------------------- 
#         Plot keys vs. index
# -----------------------------------------------------------------------------
fig = plt.figure(3, clear=True, figsize=(12, 6))
N = 1000
gs = GridSpec(nrows=1, ncols=2)
for i, dist in enumerate(['p', 'zipf']):
    ax = fig.add_subplot(gs[i])
    for name in ST_names:
        ax.scatter(np.arange(N), drivers[(dist, name, N)].t.keys(),
                   alpha=0.5,
                   label=name)
    ax.set(title='Zipf' if dist == 'zipf' else '$1/2^i$',
           xlabel='index',
           ylabel='key')
    ax.grid('on')
    ax.legend(loc='lower right')

gs.tight_layout(fig)
if SAVE_FIGS:
    fig.savefig(fig_dir.joinpath('self_org_keys.pdf'))

# ----------------------------------------------------------------------------- 
#         Plot the probability distributions
# -----------------------------------------------------------------------------
# TODO count inversions in each array to determine "sortedness"
N = 1000
keys = np.arange(1, N+1)  # function of N alone

p = 1 / (2.0**keys)
zipf = 1 / (keys * SelfOrganizingDriver.H_N(keys))

fig = plt.figure(4, clear=True)
ax = fig.add_subplot()
ax.plot(keys, p, label=r'$\frac{1}{2^i}$')
ax.plot(keys, zipf, label=r'$\frac{1}{i H_N}$')
ax.set(xlabel=r'$i^{th}$ key',
       ylabel='P(i)',
       xscale='log',
       yscale='log',
       ylim=(1e-12, 1))
ax.legend(fontsize=16)
ax.grid()
fig.tight_layout()

if SAVE_FIGS:
    fig.savefig(fig_dir.joinpath('self_org_dists.pdf'))


plt.show()

# =============================================================================
# =============================================================================
