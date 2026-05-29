#!/usr/bin/env python3
# =============================================================================
#     File: parking_problem.py
#  Created: 2022-05-03 15:25
#   Author: Bernie Roesler
# =============================================================================

r"""Exercise 3.4.43: Parking Problem.

Test hypothesis that the total cost to insert *M* random keys into a table of
size *M* is:

.. math::
    \text{cost} \sim \sqrt{\frac{\pi}{2}} M^{3/2}
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from tqdm import tqdm

from algs.search.hash import LinearProbingHashST

π = np.pi
rng = np.random.default_rng(seed=56)

# Insert N random non-negative integers into a table of size N/100.
Ms = np.logspace(1, 5, 10).astype(int)
costs = []

for M in tqdm(Ms):
    keys = rng.random(M)
    st = LinearProbingHashST(M=M, resize=False)

    # Compute the total cost of adding all keys to the table
    tot_cost = 0
    for k in tqdm(keys, desc=f'M={M}', leave=False):
        st[k] = None
        tot_cost += st._cost

    costs.append(tot_cost)

costs = np.r_[costs]

# Theoretical cost curve
ms = np.logspace(1, np.log10(max(Ms)))


def th_cost(M):
    """Theoretical cost curve."""
    c = (π / 2) ** 0.5
    return c * M ** (3 / 2)


# Fit function to the data in log-space
def fit_func(M, c, λ):
    """Fit function in log-space."""
    return λ * np.log(c * M)


popt, pcov = curve_fit(fit_func, Ms, np.log(costs), p0=(np.sqrt(π / 2), 3 / 2))
N_std = 2  # std from mean
perr = N_std * np.sqrt(np.diag(pcov))


# Apply it in linear space
def fit_costs(M, c, λ):
    """Fit function in linear space."""
    return c * M**λ


# -----------------------------------------------------------------------------
#         Plots
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()

# Theory curve
ax.plot(ms, th_cost(ms), 'C3-', label=r'$\sqrt{\frac{\pi}{2}} M^{3/2}$')

# Fit curve
ax.plot(ms, fit_costs(ms, *popt), 'C0-', label=rf"${popt[0]:.2g} M^{{{popt[1]:.3g}}}$")
# Error bounds
p0 = fit_costs(ms, *(popt + perr))
p1 = fit_costs(ms, *(popt - perr))
ax.fill_between(ms, p0, p1, color='C0', alpha=0.2)

# Data
ax.scatter(Ms, costs, c='k')

ax.set(xlabel='M', ylabel='Total Cost of Inserting M Keys', xscale='log', yscale='log')
ax.legend()
ax.grid(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.show()

# =============================================================================
# =============================================================================
