#!/usr/bin/env python3
#==============================================================================
#     File: test_qsort.py
#  Created: 2019-04-08 22:42
#   Author: Bernie Roesler
#
"""
  Description: A battery of tests for qsort certification.
"""
#==============================================================================

import sys

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np

from collections import defaultdict

from algs.sort import qsort

N = 100
m = 2**5

dist_names = ['sawtooth', 'rand', 'stagger', 'plateau', 'shuffle']
dists = defaultdict(lambda: np.zeros(N))

for name in dist_names:
    x = dists[name]  # pointer to dict
    j = 0
    k = 1
    for i in range(N):
        if name == 'sawtooth':  x[i] = i % m
        elif name == 'rand':    x[i] = np.random.randint(N)
        elif name == 'stagger': x[i] = (i*m + i) % m
        elif name == 'plateau': x[i] = min(i, m)
        elif name == 'shuffle':
            if np.random.randint(2*N) % m:
                x[i] = j
                j += 2
            else:
                x[i] = k
                k += 2

fig = plt.figure(1, clear=True)
gs = GridSpec(1, len(dists))

for i, name in enumerate(dists):
    x = dists[name]
    ax = plt.subplot(gs[i])
    ax.bar(range(len(x)), x / np.max(x))
    ax.set_title(name)

plt.suptitle(f"N = {N}, m = {m}")
plt.show()

#==============================================================================
#==============================================================================
