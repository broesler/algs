#!/usr/bin/env python3
# =============================================================================
#     File: interval2d.py
#  Created: 2022-06-09 23:50
#   Author: Bernie Roesler
#
"""
Exercise 1.2.3 Interval2D client to generate N random boxes and compute the
intersections and contains.
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np

from algs.adt import Interval2D

rng = np.random.default_rng(seed=565656)
N = 5
lo = 0.1  # contraints on width and height
hi = 0.7

# Generate N random width/heights in the unit square
whs = lo + (hi - lo) * rng.random((N, 2))

boxes = []
for w, h in whs:
    # Define endpoints of intervals within the unit sqare
    x0 = (1 - w) * rng.random()
    y0 = (1 - h) * rng.random()
    x1, y1 = x0 + w, y0 + h
    boxes.append(Interval2D(x0, y0, x1, y1))

# Naïve O(N²) algorithm
intersects = 0
contains = 0
for i in range(N):
    for j in range(i):
        if boxes[i].intersects(boxes[j]):
            intersects += 1
        if boxes[i].is_inside(boxes[j]) or boxes[j].is_inside(boxes[i]):
            contains += 1

print(f"{N = }\n"
      + f"{intersects = }\n"
      + f"{contains = }")

# -----------------------------------------------------------------------------
#         Plot
# -----------------------------------------------------------------------------
fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()

for b in boxes:
    b.draw(edgecolor='C0', facecolor='C0', alpha=0.2)

ax.set(xlabel='x', xlim=(-0.02, 1.02),
       ylabel='y', ylim=(-0.02, 1.02),
       aspect='equal',)
ax.grid(False)

plt.show()

# =============================================================================
# =============================================================================
