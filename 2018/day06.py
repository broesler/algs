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

#==============================================================================
#==============================================================================
