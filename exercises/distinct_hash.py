#!/usr/bin/env python3
# =============================================================================
#     File: distinct_hash.py
#  Created: 2022-04-25 23:57
#   Author: Bernie Roesler
# =============================================================================

r"""Exercise 3.4.8: Expectation of distinct keys in a hash table.

The expected number of free slots in the hash table using separate chaining.
The number of distinct elements in an array of
*N* integers on *[0, M-1]*  is.

.. math::
    \alpha = \frac{N}{M}
    P(\alpha) = 1 - e^{-\alpha}
    \text{\\# distinct} = MP = M (1 - e^{-\alpha})

Therefore, the number of duplicates must be:

.. math::
    \text{(\\# distinct) + (\\# duplicates)} = N
    \begin{align}
        \text{\\# duplicates} &= N - M P
                             &= N - M (1 - e^{-\alpha})
    \\end{align}

The number of free slots is the total number of slots less the number of
distinct elements:

.. math::
    \begin{align}
        \text{\\# free slots} &= M - MP
                             &= M (1 - P)
                             &= M (1 - (1 - e^{-\alpha}))
                             &= M e^{\alpha}
    \\end{align}

These values can also be computed as a fraction of the total slots *M*:

.. math::
    \text{fraction distinct} = P
    \text{fraction duplicate} = \alpha - P
    \text{fraction free} = 1 - P

See Also
--------
Exercise 2.5.31: Duplicates: Count duplicates in random integer lists.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from duplicates import count_both_sort

from algs.search.hash import SeparateChainingHashST

rng = np.random.default_rng(seed=56)

M = 97  # choose a prime
st = SeparateChainingHashST(M=M)

Ns = np.r_[[10**e for e in range(7)]]
ds = np.zeros(len(Ns))
for i, n in enumerate(Ns):
    keys = rng.random(size=n)  # floats
    ints = np.r_[[st._hash(k) for k in keys]]
    _, ds[i] = count_both_sort(ints)

free_slots = M - ds

df = pd.DataFrame(
    data=np.c_[Ns / M, free_slots], index=Ns, columns=['α', 'free']
).astype({'free': int})

df['α'] = df['α'].map("{:.2g}".format)
print(f"{M = }:")
print(df)

# -----------------------------------------------------------------------------
#         Plots
# -----------------------------------------------------------------------------
N = np.linspace(0, 5 * M)
α = N / M
P = 1 - np.exp(-α)

fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()

# Asymptotes
ax.plot(α, α - 1, 'k--', lw=1)
ax.axhline(1, c='k', ls='--', lw=1)

# Exponentials
ax.plot(α, P, label=r'Distinct = $M(1 - e^{-\alpha})$')
ax.plot(α, α - P, label=r'Duplicate = $N - M(1 - e^{-\alpha})$')
ax.plot(α, 1 - P, label=r'Free Slots = $Me^{-\alpha}$')

ax.grid()
ax.set(
    xlabel=r'$\alpha = \dfrac{N}{M}$',
    ylabel='Fraction of (Distinct/Duplicate) vs. M slots',
)
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
ax.legend()

plt.show()

# =============================================================================
# =============================================================================
