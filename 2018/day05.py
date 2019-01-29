#!/Users/bernardroesler/anaconda3/envs/insight/bin/python3
#==============================================================================
#     File: day05.py
#  Created: 2019-01-09 22:24
#   Author: Bernie Roesler
#
"""
  Description:
"""
#==============================================================================

import hashlib
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.gridspec import GridSpec

def my_hash(s):
    """Hash a string using MD5 hash function."""
    return hashlib.md5(s.encode('utf-8')).hexdigest()

# TODO this is an O(n^2) algorithm... reduce to O(n)!?
def reduce_polymer(data):
    """Perform reaction algorithm on polymer string."""
    pm = data  # initialize to input polymer
    while len(pm) > 1:
        # React first pair until no changes are made
        reduced_pm = first_pair(pm)
        if my_hash(reduced_pm) == my_hash(pm):
            return reduced_pm
        else:
            pm = reduced_pm

def first_pair(pm):
    """React the first possible pair of mers, return the resulting polymer."""
    for i, a in enumerate(pm[:-1]):
        b = pm[i+1]
        if is_react_pair(a, b):
            return pm[:i] + pm[i+2:]
    return pm  # no pairs found

def is_react_pair(a, b):
    """Determine if two mers should eliminate each other. If they are the same
    character, but opposite case, they react."""
    if a.isupper():
        if b.islower() and (a == b.upper()):
            return True
    else:
        if b.isupper() and (a == b.lower()):
            return True
    return False

#------------------------------------------------------------------------------ 
#       Main 
#------------------------------------------------------------------------------
filename = 'data/input05.dat'

with open(filename, 'r') as file:
    lines = [x.rstrip() for x in file.readlines()]
    if len(lines) == 1:
        data = lines[0]
    
# Reduce polymer string
# rp = reduce_polymer(data)
# print("Length = {:d}".format(len(rp)))  # Length = 11636

#==============================================================================
#==============================================================================
