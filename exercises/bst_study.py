#!/usr/bin/env python3
# =============================================================================
#     File: bst_study.py
#  Created: 2021-02-22 15:13
#   Author: Bernie Roesler
#
r"""
  Description: Ex 3.2.39 and 3.2.40. Tests of number of compares for search
    hits and search misses in a BST, as compared to the theoretical value::

        2 \lg N + 2 \gamma = 3 \approx 1.39 \lg N - 1.85

    where $\gamma = 0.57721...$ is *Euler's constant*.

    Estimates the average BST height for multiple values of N, as compared to
    the theoretical value::

        2.99 \lg N.

    This study also incorporates Ex 3.3.43, 3.3.44, and 3.3.46 to compare BSTs
    with RedBlackBSTs. In a 2-3 tree, the expected average search time is::

        \lg N - 0.5

    and the expected height is::

        ~ 1.0 \lg N.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from pathlib import Path
from scipy.optimize import curve_fit
from tqdm import tqdm

from algs.search import BST, RedBlackBST

FORCE_UPDATE = False
SAVE_FIGS = False

pickle_file = Path('./pkl/bst_compares_tiny.pkl')
N_trials = 30
ops = [int(x) for x in [1e2, 1e3, 1e4]]

# pickle_file = Path('./pkl/bst_compares_1e4.pkl')
# N_trials = 1000
# ops = [int(x) for x in np.logspace(2, 4)]

M = len(ops)

idx = pd.MultiIndex.from_product([list(range(N_trials)), ops])
cols = ['comps', 'heights', 'ipls']
dfs = list()

if FORCE_UPDATE or not pickle_file.exists():
    for ST, tag in zip([BST, RedBlackBST], ['bst', 'rbst']):
        # Store all data in one frame
        df = pd.DataFrame(index=idx, columns=cols,
                          data=np.zeros((len(idx), len(cols))))
        df.index.names = ['trial', 'N']

        print(f"Running {ST.__name__}...")

        # Seed the rng for consistency
        rng = np.random.default_rng(seed=565656)

        # Run the experiments
        for N in ops:
            print(f"N = {N}...")
            for i in tqdm(range(N_trials)):
                st = ST()
                tot_comp = 0
                for k in rng.random(N):
                    st[k] = 1  # set an arbitrary value
                    tot_comp += st._cost
                assert st.size() == N

                # Store stats for averages
                df.loc[i, N]['comps'] = tot_comp / N
                df.loc[i, N]['heights'] = st.height
                df.loc[i, N]['ipls'] = st.internal_path_length / N + 1

        df['tag'] = tag
        dfs.append(df)

    print(f"Writing to '{pickle_file}'...")
    df = (pd.concat(dfs)
            .pivot(columns='tag')
            .swaplevel(axis=1)
            .sort_index(axis=1)
          )
    df.to_pickle(pickle_file)

# -----------------------------------------------------------------------------
#         Plots
# -----------------------------------------------------------------------------
theory_dict = dict(# bst_avg_comps=dict(eqn=lambda N: 2*np.log2(N) + 2*np.euler_gamma - 3,
                   #                   label=r'$2 \lg N + 2\gamma - 3$'),
                   bst_avg_comps=dict(eqn=lambda N: 1.39 * np.log2(N) - 1.85,
                                      label=r'$1.39 \lg N - 1.85$'),
                   bst_avg_ipls=dict(eqn=lambda N: 1.39 * np.log2(N) - 1.85,
                                     label=r'$1.39 \lg N - 1.85$'),
                   bst_avg_heights=dict(eqn=lambda N: 2.99 * np.log2(N),
                                        label=r'$2.99 \lg N$'),
                   rbst_avg_comps=dict(eqn=lambda N: np.log2(N) - 0.5,
                                       label=r'$\lg N - 0.5$'),
                   rbst_avg_ipls=dict(eqn=lambda N: np.log2(N) - 0.5,
                                      label=r'$\lg N - 0.5$'),
                   rbst_avg_heights=dict(eqn=lambda N: np.log2(N),
                                         label=r'$\lg N$'),
                   )

titles = dict(bst='BST', rbst='Red-Black BST')
opts = dict(comps=dict(ylim=20, ylabel='compares'),
            heights=dict(ylim=40, ylabel='height'),
            ipls=dict(ylim=20, ylabel='internal path length'))

fig = plt.figure(1, clear=True)
fig.set_size_inches((8, 8), forward=True)
gs = fig.add_gridspec(nrows=3, ncols=2)
plt.rc('font', **{'size': 8})

df = pd.read_pickle(pickle_file)

for j, tag in enumerate(['bst', 'rbst']):
    for i, col_name in enumerate(cols):
        # FIXME average compares are too low by 1 vs IPL
        # if col_name == 'comps':
        #     df[col_name] += 1

        # Aggregate the mean and std
        g = df[tag].groupby('N').agg(['mean', 'std'])

        # Theory curve
        x = np.logspace(np.log10(min(ops)), np.log10(max(ops)))

        # Fit curve to data
        def func(x, a, b):
            return a * np.log2(x) + b

        popt, pcov = curve_fit(func, g.index, g[col_name, 'mean'])

        # -----------------------------------------------------------------------------
        #         Make Plots
        # -----------------------------------------------------------------------------
        ax = fig.add_subplot(gs[i, j])

        if i == 0:
            ax.set_title(titles[tag])

        # Plot the theoretical curves, and the curve fit to the data
        ax.plot(x, func(x, *popt), color='k', ls='-',
                label=fr"${popt[0]:.2f} \lg N {popt[1]:+.2f}$")
        ax.annotate(rf"$\leftarrow$ {func(x, *popt)[-1]:.0f}",
                    xy=(max(ops) + 100, func(x, *popt)[-1]),
                    ha='left', va='center', color='k')

        y_theory = theory_dict[f"{tag}_avg_{col_name}"]['eqn'](x)
        label = theory_dict[f"{tag}_avg_{col_name}"]['label']

        ax.plot(x, y_theory, color='C3', ls='-', label=label)
        ax.annotate(rf"$\leftarrow$ {y_theory[-1]:.0f}",
                    xy=(max(ops) + 100, y_theory[-1]),
                    ha='left', va='center', color='C3')

        # Plot the runtime distributions
        sns.scatterplot(ax=ax, data=df[tag].reset_index(), x='N', y=col_name,
                        color=0.5*np.ones(3), s=10, alpha=0.10)

        # Plot the means and stds of each group
        sns.scatterplot(ax=ax, data=g[col_name], x='N', y='mean',
                        color='k', marker='d', s=30, zorder=3)

        for N, m in g[col_name].iterrows():
            ax.plot((N, N), (m['mean'] - m['std'], m['mean'] + m['std']),
                    c='k', ls='-', lw=2, alpha=1.0)

        ax.legend(loc='lower right')

        # Format axes
        xlim = ax.get_xlim()
        # ylim = ax.get_ylim()  # [0, 20]
        ylim = [0, opts[col_name]['ylim']]

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

        # Hide y-labels except for left
        if j > 0:
            ax.yaxis.set_ticklabels([])
            ax.set_ylabel('')

        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        gs.tight_layout(fig)

        if SAVE_FIGS:
            figname = Path(f"./figures/{tag}_avg_{col_name}.pdf")
            fig.savefig(figname)

        plt.show()

# =============================================================================
# =============================================================================
