#!/usr/bin/env python3
# =============================================================================
#     File: self_org_plots.py
#  Created: 2019-11-17 11:28
#   Author: Bernie Roesler
# =============================================================================

"""Plots for Exercise 3.1.33 (self-organizing search)."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import seaborn.objects as so
from self_org_driver import SelfOrganizingDriver

SAVE_FIGS = False
RANDINIT = False

sns.reset_defaults()

if SAVE_FIGS:
    plt.close('all')  # FacetGrid does not have a `clear` option.
    fig_dir = Path(__file__).parent / 'figures'

# Load the data
PKL_DIR = Path(__file__).parent / 'pkl'

tag = '_randinit' if RANDINIT else ''

# Load the parquet files
df_file = PKL_DIR / "self_org_data.parquet"
df = pd.read_parquet(df_file)

kf_file = PKL_DIR / "self_org_keys.parquet"
kf = pd.read_parquet(kf_file)

df = df[df['randinit'] == RANDINIT]
kf = kf[kf['randinit'] == RANDINIT]

tots = df.melt(
    id_vars=['dist', 'ST', 'N'],
    value_vars=['put', 'get'],
    var_name='op',
    value_name='runtime [s]',
)

# -----------------------------------------------------------------------------
#         Plot distributions of runtimes
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(num=1, clear=True)

st_order = df["ST"].cat.categories.array

sp = (
    so.Plot(df, x="N", y="runtime", color="ST")
    .add(so.Dots(alpha=0.25), so.Jitter(0.1), so.Dodge(), legend=False)
    # TODO how to get Dot/Range as "palette='dark'" like in pointplot?
    .add(so.Dot(marker="d", pointsize=9, edgecolor="w"), so.Agg("mean"), so.Dodge())
    .add(so.Range(), so.Est(errorbar=("ci", 95)), so.Dodge())
    .scale(x=so.Nominal(), y="log", color=so.Nominal(order=st_order))
    .theme(plt.rcParams | {"axes.grid.which": "both"})
    .on(ax)
    .plot(pyplot=True)
)

leg = sp._figure.legends[0]
handles, labels = leg.legend_handles, [x.get_text() for x in leg.texts]
del sp._figure.legends[0]
ax.legend(handles, labels, title='Symbol Table', loc='upper left')

if SAVE_FIGS:
    fig.savefig(fig_dir / f"self_org_timedists{tag}.pdf")

# -----------------------------------------------------------------------------
#         Plot total runtimes
# -----------------------------------------------------------------------------
fig = plt.figure(2, clear=True)
fig.set_size_inches((8, 6.4), forward=True)

sp = (
    so.Plot(tots, x='N', y='runtime [s]', color='ST')
    .facet(row='op', col='dist')
    .add(so.Line(marker='o'))
    .scale(x='log', y='log')
    .layout(engine="constrained")
    .theme(plt.rcParams | {"axes.spines.top": False, "axes.spines.right": False})
    .on(fig)
    .plot()
    # .plot(pyplot=True)
    # NOTE need .plot(pyplot=True) to place legend inside the figure. See:
    # <https://github.com/mwaskom/seaborn/blob/32088bbc3adc611b7118e57fce6d4ed096a76a29/seaborn/_core/plot.py#L1750-L1754>  # noqa: E501
)

# sp._figure.get_layout_engine().set(rect=(0, 0, 0.8, 1))

# Move the legend into the axes
leg = sp._figure.legends[0]
handles, labels = leg.legend_handles, [x.get_text() for x in leg.texts]
del sp._figure.legends[0]
ax = sp._figure.axes[-1]
ax.legend(handles, labels, loc='lower right')

if SAVE_FIGS:
    fig.savefig(fig_dir / f"self_org_tots{tag}.pdf")

# -----------------------------------------------------------------------------
#         Plot keys vs. index
# -----------------------------------------------------------------------------
fig = plt.figure(3, clear=True)
fig.suptitle('Keys vs. Index')
fig.set_size_inches((9, 5.4), forward=True)

kf['title'] = kf['dist'].map({'p': r'$1 / 2^i$', 'zipf': 'Zipf: $1 / (i H_N)$'})

sp = (
    so.Plot(kf, x='idx', y='keys', color='ST')
    .facet(col='title')
    .add(so.Dot(alpha=0.5))
    .label(x="index", title=lambda x: rf"{x}")
    .layout(engine="constrained")
    .theme(plt.rcParams | {"axes.grid": True})
    .on(fig)
    .plot()
)

for ax in sp._figure.axes:
    ax.set_aspect("equal")

# sp._figure.get_layout_engine().set(rect=(0, 0, 0.8, 1))

# Move the legend into the axes
leg = sp._figure.legends[0]
handles, labels = leg.legend_handles, [x.get_text() for x in leg.texts]
del sp._figure.legends[0]
ax = sp._figure.axes[0]
ax.legend(handles, labels, loc='lower right')

if SAVE_FIGS:
    fig.savefig(fig_dir / f"self_org_keys{tag}.pdf")

# -----------------------------------------------------------------------------
#         Plot the probability distributions
# -----------------------------------------------------------------------------
# TODO count inversions in each array to determine "sortedness"
N = kf['keys'].max()  # max key value, which is N for the p and zipf dists
keys = np.arange(1, N + 1)  # function of N alone

p = 1 / (2.0**keys)
zipf = 1 / (keys * SelfOrganizingDriver.H_N(keys))

fig = plt.figure(4, clear=True)
ax = fig.add_subplot()
ax.plot(keys, p, label=r'$\frac{1}{2^i}$')
ax.plot(keys, zipf, label=r'$\frac{1}{i H_N}$')
ax.set(
    xlabel=r'$i^{th}$ key', ylabel='P(i)', xscale='log', yscale='log', ylim=(1e-12, 1)
)
ax.legend(fontsize=16)
ax.grid(True, which='both')

if SAVE_FIGS:
    fig.savefig(fig_dir / f"self_org_dists{tag}.pdf")


plt.show()

# =============================================================================
# =============================================================================
