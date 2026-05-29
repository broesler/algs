#!/usr/bin/env python3
# =============================================================================
#     File: exercises/count_reds.py
#  Created: 2021-03-25 12:28
#   Author: Bernie Roesler
# =============================================================================

"""Ex 3.3.42 and 3.3.45. Compute the percentage of red nodes in a given
red-black BST, and count the number of rotations and node splits used to build
the tree.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.optimize import curve_fit
from tqdm import tqdm

from algs.search import RedBlackBST

FORCE_UPDATE = False
SAVE_FIGS = False

PKL_PATH = Path(__file__).parent / "pkl"

size_name = "tiny"
N_trials = 30
ops = [int(x) for x in [1e2, 1e3, 1e4]]

# size_name = "1e4"
# N_trials = 1000
# ops = [int(x) for x in np.logspace(2, 4)]

pickle_file = PKL_PATH / f"rbst_reds_{size_name}.pkl"

M = len(ops)

idx = pd.MultiIndex.from_product([list(range(N_trials)), ops])
cols = ['reds', 'rotations', 'splits']
df = pd.DataFrame(index=idx, columns=cols,
                  data=np.zeros((len(idx), len(cols))))
df.index.names = ['trial', 'N']

if FORCE_UPDATE or not pickle_file.exists():
    # Seed the rng for consistency
    rng = np.random.default_rng(seed=565656)
    # Run the experiments
    for N in ops:
        print(f"N = {N}...")
        for i in tqdm(range(N_trials)):
            st = RedBlackBST.fromkeys(rng.random(N))
            # Store stats for averages
            df.loc[(i, N), 'reds'] = st.Nred / N
            df.loc[(i, N), 'rotations'] = st.Nrotations / N
            df.loc[(i, N), 'splits'] = st.Nsplits / N

    print(f"Writing to '{pickle_file}'... ", end='')
    df.to_pickle(pickle_file)
    print('done.')
else:
    df = pd.read_pickle(pickle_file)


# -----------------------------------------------------------------------------
#         Plots
# -----------------------------------------------------------------------------
opts = {"reds": {"ylabel": 'red nodes'},
            "rotations": {"ylabel": 'rotations'},
            "splits": {"ylabel": 'splits'}}

fig = plt.figure(1, clear=True)
gs = fig.add_gridspec(nrows=3, ncols=1)

for i, col_name in enumerate(cols):
    # Aggregate the mean and std
    g = df.groupby('N').agg(['mean', 'std'])

    # Fit curve to data
    x = np.logspace(np.log10(min(ops)), np.log10(max(ops)))

    def func(x, a, b):
        """Model function for curve fit."""
        return a * x + b

    popt, pcov = curve_fit(func, g.index, g[col_name, 'mean'])

    # -----------------------------------------------------------------------------
    #         Make Plots
    # -----------------------------------------------------------------------------
    ax = fig.add_subplot(gs[i])

    # Plot the curve fit to the data
    ax.plot(x, func(x, *popt), color='k', ls='-',
            label=fr"${popt[0]:.2f} N {popt[1]:+.2f}$")
    ax.annotate(rf"$\leftarrow$ {func(x, *popt)[-1]:.2f}",
                xy=(max(ops) + 100, func(x, *popt)[-1]),
                ha='left', va='center', color='k')

    # Plot the runtime distributions
    sns.scatterplot(ax=ax, data=df[col_name].reset_index(), x='N', y=col_name,
                    color=0.5*np.ones(3), s=10, alpha=0.30)

    # Plot the means and stds of each group
    sns.scatterplot(ax=ax, data=g[col_name], x='N', y='mean',
                    color='k', marker='d', s=30, zorder=3)

    for N, m in g[col_name].iterrows():
        ax.plot((N, N), (m['mean'] - m['std'], m['mean'] + m['std']),
                c='k', ls='-', lw=2, alpha=1.0)

    ax.legend(loc='lower right')

    # Format axes
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    # ylim = [0, opts[col_name]['ylim']]

    ax.xaxis.label.set(color='C3')
    ax.yaxis.label.set(color='C3')
    ax.set_xticks([min(ops), max(ops)])
    ax.set_yticks([0, round(ylim[1])])

    # Place labels on axis (like ticklabels)
    ax.set_xlabel('operations')
    ax.xaxis.set_label_coords(np.mean(xlim), 0,
                            transform=ax.xaxis.get_ticklabels()[0].get_transform())

    ax.set_ylabel(opts[col_name]['ylabel'])
    ax.yaxis.set_label_coords(0, ylim[1] / 2,
                            transform=ax.yaxis.get_ticklabels()[0].get_transform())

    # Hide x-labels except for bottom
    if i < 2:
        ax.xaxis.set_ticklabels([])
        ax.set_xlabel('')
    else:
        ax.ticklabel_format(style='plain')  # no scientific notation

    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    gs.tight_layout(fig)

if SAVE_FIGS:
    FIG_PATH = Path(__file__).parent / "figures"
    figname = FIG_PATH / f"rbst_avg_reds_{size_name}.pdf"
    fig.savefig(figname)

plt.show()

# =============================================================================
# =============================================================================
