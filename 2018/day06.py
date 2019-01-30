#!/Users/bernardroesler/anaconda3/envs/insight/bin/python3
#==============================================================================
#     File: day06.py
#  Created: 2019-01-28 22:39
#   Author: Bernie Roesler
#
"""
  Description: Manhattan Areas
"""
#==============================================================================

import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns

pat = re.compile(r'(\d+), (\d+)')

def parse(line):
    """Convert string '123, 45\n' to tuple of integers (123, 45)."""
    data = line.rstrip()
    res = pat.match(data)
    x, y = int(res.group(1)), int(res.group(2))
    return (x, y)

filename = './data/input06.dat'
with open(filename, 'r') as file:
    coords = [parse(x) for x in file.readlines()]

# Brute force:
#  1. create grid that is x% larger than max dimensions
#  2. run k-NN (for k = 1) on the grid, where centroids are given
#  3. count points labeled in each class
#  4. take maximum count, excluding convex hull of centroids
#

# Plots
x, y = list(zip(*coords))  # transpose to two lists
plt.scatter(x, y)
plt.show()
#==============================================================================
#==============================================================================
