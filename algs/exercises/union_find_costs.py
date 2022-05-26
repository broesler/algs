#!/usr/bin/env python3
# =============================================================================
#     File: union_find_costs.py
#  Created: 2022-05-25 19:36
#   Author: Bernie Roesler
#
"""
Amortized cost plots of the union-find datatypes.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from algs.unionfind import (read_uf_file, QuickFindUF, QuickUnionUF,
                            WeightedQuickUnionUF, WeightedQuickFindUF)

file = Path('./data/mediumUF.txt')
N, items = read_uf_file(file)
M = len(items)      # total number of connections
ops = 1 + np.arange(M)  # number of operations

# Manually iterate through connections to track costs along the way
uf = QuickFindUF(N)
costs = list()
totals = list()
for p, q in items:
    if uf.connected(p, q):
        costs.append(uf._cost)
        totals.append(uf._total)
        continue
    uf.union(p, q)
    costs.append(uf._cost)
    totals.append(uf._total)

tots = totals / ops

fig = plt.figure(1, clear=True, constrained_layout=True)
fig.set_size_inches((5, 8), forward=True)
ax = fig.add_subplot()
ax.scatter(ops, costs, color=0.7*np.r_[1, 1, 1], s=1, alpha=0.8)
ax.scatter(ops, tots, c='C3', s=1, alpha=0.8)

ax.annotate(rf"{tots[-1]:.0f}",
            xy=(M, tots[-1]), xycoords='data',
            xytext=(1.1*M, 1.1*tots[-1]), textcoords='data',
            ha='center', va='bottom', color='C3',
            arrowprops=dict(arrowstyle="-|>", color="C3"))

ax.set_xlabel('number of connections', color='C3', labelpad=-10)
ax.set_ylabel('number of array references', color='C3', labelpad=-25)
ax.set_xlim((0, M))
ax.set_xticks((0, M))
y_max = int(np.ceil(max(costs) / 100) * 100)
ax.set_ylim((0, y_max))
ax.set_yticks((0, y_max))

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.show()
# =============================================================================
# =============================================================================
