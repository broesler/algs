#!/usr/bin/env python3
#==============================================================================
#     File: day03.py
#  Created: 2018-12-17 21:27
#   Author: Bernie Roesler
#
"""
  Description:
"""
#==============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

import re

filename = "data/day03.txt"

# Compile claim parser ahead of time
pat = re.compile(r"#(\d+)\s*@\s*(\d+),(\d+):\s*(\d+)x(\d+)")

def parse_claim(claim):
    """Get relevant numbers out of the claim string."""
    m = pat.match(claim)
    g = tuple(int(x) for x in m.groups())
    if m:
        return g[0], np.array(g[1:3]), np.array(g[3:5])
    else:
        return None, None, None

ids = list()  # [int] claim id
xys = list()  # (int, int) origin tuple, top-left corner is (0,0)
whs = list()  # (int, int) width, height tuple
max_x = 0
max_y = 0
with open(filename, 'r') as f:
    for line in f:
        claim = line.rstrip()
        claim_id, xy, wh = parse_claim(claim)
        ids.append(claim_id)
        xys.append(xy)
        whs.append(wh)
        # Track canvas dimensions
        x, y = xy + wh
        max_x = max(x, max_x)
        max_y = max(y, max_y)

# Populate canvas
# TODO HUGE memory requirement if canvas gets big... need more clever algorithm
canvas = np.zeros([max_x, max_y])
for xy, wh in zip(xys, whs):
    rows = slice(xy[0], xy[0] + wh[0])
    cols = slice(xy[1], xy[1] + wh[1])
    canvas[rows, cols] += 1

#------------------------------------------------------------------------------ 
#        Part 1
#------------------------------------------------------------------------------
# How many square inches of fabric are within two or more claims?
overlaps = np.int(np.sum(canvas > 1))
print(f"Overlap = {overlaps:d} [in^2]")

#------------------------------------------------------------------------------ 
#        Part 2
#------------------------------------------------------------------------------
# What is the ID of the only claim that doesn't overlap?
# Search canvas for range that is all ones
the_one = -1
for i, xy, wh in zip(ids, xys, whs):
    rows = slice(xy[0], xy[0] + wh[0])
    cols = slice(xy[1], xy[1] + wh[1])
    if (canvas[rows, cols] == 1).all():
        the_one = i
        break

print(f"The One ID = {the_one:d}")

# Fun plots
from scipy.interpolate import griddata
X, Y = np.meshgrid(np.arange(max_x), np.arange(max_y), indexing='ij')
# grid_x, grid_y = np.meshgrid(np.linspace(0, max_x, 1000),
#                              np.linspace(0, max_y, 1000),
#                              indexing='ij')
# points = np.vstack([np.ravel(X), np.ravel(Y)]).T
# grid_z = griddata(points, np.ravel(canvas), (grid_x, grid_y), method='nearest')

fig = plt.figure(1)
fig.clf()
ax = fig.add_subplot(111)
# ax = fig.add_subplot(111, projection='3d')
# ax.plot_surface(X, Y, canvas)
# ax.plot_surface(grid_x, grid_y, grid_z)
ax.imshow(canvas, cmap='viridis')
# ax.imshow(grid_z)

plt.show()
#==============================================================================
#==============================================================================
