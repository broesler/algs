#!/usr/bin/env python3
#==============================================================================
#     File: test_antiquicksort.py
#  Created: 2019-03-21 00:12
#   Author: Bernie Roesler
#
"""
  Description:
"""
#==============================================================================

import time
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

from algs.sort import is_sorted, quicksort

# TODO separate data building from timing.
files = [('test_data/antiquicksort10K.txt',     10_000),
         ('test_data/antiquicksort20K.txt',     20_000),
         ('test_data/antiquicksort50K.txt',     50_000),
         ('test_data/antiquicksort100K.txt',   100_000)] #,
         # ('test_data/antiquicksort250K.txt',   250_000),
         # ('test_data/antiquicksort500K.txt',   500_000),
         # ('test_data/antiquicksort1M.txt',   1_000_000)]

runtimes = np.zeros([len(files), 2])
for i, f in enumerate(files):
    with open(f[0], 'r') as the_file:
        A = the_file.readlines()
    start = time.time()
    S = quicksort(A)
    stop = time.time()
    assert is_sorted(S)
    runtimes[i, :] = (f[1], stop - start)

fig = plt.figure(1, clear=False)
ax = fig.add_subplot(111)
ax.plot(runtimes[:, 0], runtimes[:, 1], 'x-')

ax.set_xscale('log')
ax.set_yscale('log')

ax.grid(b=True, which='major', c='k')
ax.grid(b=True, which='minor')

ax.set_xlabel('$N$')
ax.set_ylabel('runtime [s]')


#==============================================================================
#==============================================================================
