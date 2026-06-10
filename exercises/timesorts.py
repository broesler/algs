#!/usr/bin/env python3
# ==============================================================================
#     File: test_timesorts.py
#  Created: 2019-03-21 00:12
#   Author: Bernie Roesler
# ==============================================================================

"""Time the run of sorting algorithms."""

import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from algs.sort import (
    bubble_sort,
    heap_sort,
    insertion_sort,
    is_sorted,
    mergesort,
    mergesort_BU,
    qsort,
    # qsort0,
    # qsort1,
    # qsort2,
)

sort_funs = [bubble_sort, insertion_sort, mergesort, mergesort_BU, qsort, heap_sort]
# sort_funs = [qsort0, qsort1, qsort2, qsort]

# Define lengths of input
Nmax = 5e3
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
records = []

# Time the sort functions
pbar = tqdm(sort_funs)
for sort in pbar:
    name = sort.__name__
    pbar.set_description(name)
    for kind in masters:
        vbar = tqdm(vals, leave=False)
        for N in vbar:
            vbar.set_description(f'{kind} N={N}')
            A = masters[kind][:N]
            start = time.perf_counter_ns()
            S = sort(A)
            stop = time.perf_counter_ns()
            assert is_sorted(S)
            records.append(
                {
                    'sort': name,
                    'kind': kind,
                    'N': N,
                    'runtime [s]': (stop - start) / 1e9,
                }
            )

runtimes = pd.DataFrame(records).astype({'sort': 'category', 'kind': 'category'})
runtimes['sort'] = runtimes['sort'].cat.rename_categories(lambda x: x.replace('_', ' '))

# ------------------------------------------------------------------------------
#        Plots!
# ------------------------------------------------------------------------------
fig, ax = plt.subplots(num=1, clear=True)

sns.lineplot(
    data=runtimes,
    x='N',
    y='runtime [s]',
    hue='sort',
    style='kind',
    markers=True,
    dashes=False,
    ax=ax,
)

ax.grid(which='both')
ax.set(
    xscale='log',
    yscale='log',
)

plt.show()

print('done.')

# ==============================================================================
# ==============================================================================
