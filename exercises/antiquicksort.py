#!/usr/bin/env python3
# =============================================================================
#     File: test_antiquicksort.py
#  Created: 2019-03-21 00:12
#   Author: Bernie Roesler
# =============================================================================

"""Run quicksort on the anti-quicksort data and plot the runtimes."""

import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from algs.sort import is_sorted, quicksort0

sys.setrecursionlimit(10_000)

DATA_PATH = Path(__file__).parent.parent / 'data'

# TODO separate data building from timing.
files = [
    (DATA_PATH / 'antiquicksort10K.txt', 10_000),
    (DATA_PATH / 'antiquicksort20K.txt', 20_000),
    (DATA_PATH / 'antiquicksort50K.txt', 50_000),
    (DATA_PATH / 'antiquicksort100K.txt', 100_000),
    # (DATA_PATH / 'antiquicksort250K.txt', 250_000),
    # (DATA_PATH / 'antiquicksort500K.txt', 500_000),
    # (DATA_PATH / 'antiquicksort1M.txt', 1_000_000)]
]

runtimes = np.zeros([len(files), 2])
for i, f in enumerate(files):
    with f[0].open() as the_file:
        A = the_file.readlines()
    start = time.time()
    S = quicksort0(A)
    stop = time.time()
    assert is_sorted(S)
    runtimes[i, :] = (f[1], stop - start)

fig = plt.figure(1, clear=True)
ax = fig.add_subplot(111)
ax.plot(runtimes[:, 0], runtimes[:, 1], 'x-')

ax.set_xscale('log')
ax.set_yscale('log')

ax.grid(which='major', c='k')
ax.grid(which='minor')

ax.set_xlabel('$N$')
ax.set_ylabel('runtime [s]')


# =============================================================================
# =============================================================================
