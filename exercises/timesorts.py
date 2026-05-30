#!/usr/bin/env python3
# ==============================================================================
#     File: test_timesorts.py
#  Created: 2019-03-21 00:12
#   Author: Bernie Roesler
# ==============================================================================

"""Time the run of sorting algorithms."""

import itertools
import time
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from algs.sort import (
    bubble_sort,
    heap_sort,
    insertion_sort,
    is_sorted,
    mergesort,
    mergesort_BU,
    qsort,
)

sort_funs = [bubble_sort, insertion_sort, mergesort, mergesort_BU, qsort, heap_sort]
# sort_funs = [qsort0, qsort1, qsort2, qsort]

# Define lengths of input
Nmax = 4e3
vals = np.power(2, np.arange(np.log2(Nmax))).astype(np.int64)
M = len(vals)

# Massive arrays from which to sample later
rng = np.random.default_rng(seed=565656)
masters = {}
masters['random'] = rng.integers(max(vals), size=max(vals))
masters['sorted'] = np.array(sorted(masters['random']))
# masters['reverse'] = np.array(masters['sorted'][::-1])
# masters['equal'] = np.ones(max(vals))
masters['binary'] = np.concatenate(
    [np.ones(max(vals // 2)), np.zeros(max(vals // 2))]
).astype(np.int64)
rng.shuffle(masters['binary'])
Ntypes = len(masters)

# Initialize dictionary
runtimes = defaultdict(lambda: defaultdict(lambda: np.zeros([M, 2])))

# Time the sort functions
for sort in sort_funs:
    name = sort.__name__
    print(f"-----{name}-----")
    for kind in masters:
        for i, N in enumerate(vals):
            A = masters[kind][:N]
            start = time.time()
            S = sort(A)
            stop = time.time()
            assert is_sorted(S)
            runtimes[name][kind][i, :] = (N, stop - start)


# ------------------------------------------------------------------------------
#        Plots!
# ------------------------------------------------------------------------------
fig = plt.figure(1, clear=True)
ax = fig.add_subplot(111)

# TODO rewrite with pandas and seaborn
colors = plt.rcParams['axes.prop_cycle']()
marker = itertools.cycle(('x', 'o', '^', 's', 'd')[:Ntypes])

for sort in sort_funs:
    name = sort.__name__
    color = next(colors)['color']
    for kind in masters:
        ax.plot(
            runtimes[name][kind][:, 0],
            runtimes[name][kind][:, 1],
            c=color,
            marker=next(marker),
            ls='-',
            label=f"{name.replace('_', ' ')}: {kind}",
        )

ax.set_xscale('log')
ax.set_yscale('log')
ax.grid(which='major', c='k')
ax.grid(which='minor')

ax.legend()
ax.set_xlabel('$N$')
ax.set_ylabel('runtime [s]')

plt.show()

print('done.')

# ==============================================================================
# ==============================================================================
