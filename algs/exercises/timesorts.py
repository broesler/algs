#!/usr/bin/env python3
#==============================================================================
#     File: test_timesorts.py
#  Created: 2019-03-21 00:12
#   Author: Bernie Roesler
#
"""
  Description: Time the run of sorting algorithms.
"""
#==============================================================================

import time
import itertools

import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict

from algs.sort import *

sort_funs = [bubble_sort, insertion_sort, mergesort, mergesort_BU,
             qsort, heap_sort]
# sort_funs = [qsort0, qsort1, qsort2, qsort]

# Define lengths of input
Nmax = 4e3
vals = np.power(2, np.arange(np.log2(Nmax))).astype(np.int64)
M = len(vals)

# Massive arrays from which to sample later
masters = dict()
masters['random'] = np.random.randint(max(vals), size=max(vals))
masters['sorted'] = np.array(sorted(masters['random']))
# masters['reverse'] = np.array(masters['sorted'][::-1])
# masters['equal'] = np.ones(max(vals))
masters['binary'] = np.concatenate([np.ones(max(vals//2)), 
                                    np.zeros(max(vals//2))]).astype(np.int64)
np.random.shuffle(masters['binary'])
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


#------------------------------------------------------------------------------ 
#        Plots!
#------------------------------------------------------------------------------
fig = plt.figure(1, clear=True)
ax = fig.add_subplot(111)

colors = ax._get_lines.prop_cycler
marker = itertools.cycle(('x', 'o', '^', 's', 'd')[:Ntypes])

for sort in sort_funs:
    name = sort.__name__
    color = next(colors)['color']
    for kind in masters:
        ax.plot(runtimes[name][kind][:, 0], runtimes[name][kind][:, 1],
                c=color, marker=next(marker), ls='-',
                label="{}: {}".format(name.replace('_', ' '), kind))

ax.set_xscale('log')
ax.set_yscale('log')
ax.grid(b=True, which='major', c='k')
ax.grid(b=True, which='minor')

ax.legend()
ax.set_xlabel('$N$')
ax.set_ylabel('runtime [s]')

plt.show()

print('done.')

#==============================================================================
#==============================================================================
