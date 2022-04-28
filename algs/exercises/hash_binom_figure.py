#!/usr/bin/env python3
# =============================================================================
#     File: hash_list_lengths.py
#  Created: 2022-04-26 22:55
#   Author: Bernie Roesler
#
"""
Plot the frequency distribution of list lengths to match figure at
top of page 468 in Sedgewick and Wayne, Algorithms, 4 ed.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path
from scipy.special import factorial
from scipy.stats import binom, poisson, chi2, chisquare

from algs.search import SeparateChainingHashST
from frequency_counter import FrequencyCounter

MINLEN = 1  # 1, 8, 10
filename = Path('../data/tale.txt')  # 779K

# Add each of the unique words in Tale of Two Cities to the hash table.
fc = FrequencyCounter(SeparateChainingHashST, M=997, resize=False)
fc.count_frequencies(filename, MINLEN)
st = fc.t

Ls = st._list_lengths()  # empirical list lengths

# Theoretical distribution of list lengths is binomial -> Poisson as N -> ∞.
α = st.N / st.M              # mean list length
k = np.linspace(0, 30, 100)  # number of keys per list
# k = np.arange(30)


# NOTE The Poisson distribution is a *discrete* distribution, so this function
# *should* be computed at integer `k` values, with a stem plot below. We'll use
# the continuous function to match the book figure.
# P(k) = poisson(mu=α).pmf(k)
def P(k):
    """Poisson distribution with parameter `k`."""
    return α**k * np.exp(-α) / factorial(k)


Pk = P(k)

# -----------------------------------------------------------------------------
#         Chi-squared test
# -----------------------------------------------------------------------------
# Chi-squared test to determine if keys are indeed distributed uniformly
the_test = chisquare(Ls, ddof=1)

# Manually calculate the test statistic and compare to the distribution
Tn = st.chi_square()  # compute the test statistic
a = 0.05
q = chi2(st.M-2).ppf(1-a)
pvalue = 1 - chi2(st.M-2).cdf(Tn)

assert np.isclose(the_test.statistic, Tn)
assert np.isclose(the_test.pvalue, pvalue)

if Tn > q:
    print("Reject H0 that keys are uniformly-distributed.")
else:
    print("Fail to reject H0 that keys are uniformly-distributed.")

print(f"{Tn     = }")
print(f"{pvalue = }")

# -----------------------------------------------------------------------------
#         Plot
# -----------------------------------------------------------------------------
fig = plt.figure(0, clear=True, constrained_layout=True)
fig.set_size_inches((12, 3), forward=True)
ax = fig.add_subplot()

# Plot the histogram of list lengths
ax.hist(Ls, bins=np.arange(31)+0.5, density=True, rwidth=0.9, color='k')

# Plot the theoretical distribution
ax.plot(k, Pk, 'C3')
# ax.stem(k, Pk, linefmt='C3-', markerfmt='C3o')

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

ax.set_xlabel(rf"list length ({st.N:,d} keys, $M$ = {st.M})", color='C3')
ax.set_ylabel('frequency', color='C3', labelpad=-25)
ax.set_yticks([0, 0.125])

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.grid(False)

plt.show()
# =============================================================================
# =============================================================================
