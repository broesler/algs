#!/Users/bernardroesler/anaconda3/bin/python3
#==============================================================================
#     File: day03.py
#  Created: 2018-12-17 21:27
#   Author: Bernie Roesler
#
"""
  Description:
"""
#==============================================================================

import numpy as np
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
    canvas[xy[0]:xy[0]+wh[0], xy[1]:xy[1]+wh[1]] += 1

# How many square inches of fabric are within two or more claims?
overlaps = np.int(np.sum(canvas > 1))
print(f"Overlap = {overlaps:d} [in^2]")

#==============================================================================
#==============================================================================
