#!/usr/bin/env python3
# ==============================================================================
#     File: test_qsort.py
#  Created: 2019-04-08 22:42
#   Author: Bernie Roesler
# ==============================================================================

"""A battery of tests for qsort certification."""

from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

N = 100
m = 2**5

dist_names = ['sawtooth', 'rand', 'stagger', 'plateau', 'shuffle']
dists = defaultdict(lambda: np.zeros(N))

rng = np.random.default_rng(seed=56)

for name in dist_names:
    x = dists[name]  # pointer to dict
    j = 0
    k = 1
    for i in range(N):
        if name == 'sawtooth':
            x[i] = i % m
        elif name == 'rand':
            x[i] = rng.integers(N)
        elif name == 'stagger':
            x[i] = (i * m + i) % m
        elif name == 'plateau':
            x[i] = min(i, m)
        elif name == 'shuffle':
            if rng.integers(2 * N) % m:
                x[i] = j
                j += 2
            else:
                x[i] = k
                k += 2

fig = plt.figure(1, clear=True)
gs = fig.add_gridspec(1, len(dists))

for i, name in enumerate(dists):
    x = dists[name]
    ax = plt.subplot(gs[i])
    ax.bar(range(len(x)), x / np.max(x))
    ax.set_title(name)

plt.suptitle(f"N = {N}, m = {m}")
plt.show()

# ==============================================================================
# ==============================================================================
