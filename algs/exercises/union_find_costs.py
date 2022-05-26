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
from tqdm import tqdm

from algs.unionfind import (read_uf_file, QuickFindUF, QuickUnionUF,
                            WeightedQuickUnionUF, WeightedQuickFindUF)

file = Path('./data/mediumUF.txt')
N, items = read_uf_file(file)
M = len(items)  # total number of connections
ops = np.arange(M)  # number of operations

# Manually iterate through connections to track costs along the way
uf = QuickFindUF(N)
costs = list()
totals = list()
for p, q in tqdm(items):
    if uf.connected(p, q):
        costs.append(uf._cost)
        totals.append(uf._total)
        continue
    uf.union(p, q)
    costs.append(uf._cost)
    totals.append(uf._total)


fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()
ax.scatter(ops, costs, c='k', alpha=0.5)
ax.scatter(ops[1:], totals[1:] / ops[1:], c='C3', alpha=0.5)

ax.set_xlabel('number of connections', color='C3')
ax.set_ylabel('number of array references', color='C3')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.show()
# =============================================================================
# =============================================================================
