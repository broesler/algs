#!/usr/bin/env python3
#==============================================================================
#     File: day05.py
#  Created: 2019-01-09 22:24
#   Author: Bernie Roesler
#
"""
  Description: String reduction algorithm
"""
#==============================================================================

from basics.stack import Stack

def reduce_polymer(polymer):
    """Perform reaction algorithm on polymer string."""
    rp = Stack()  # initialize reduced polymer output
    for mer in polymer:
        if rp.is_empty:
            rp.push(mer)
            continue

        # Pop the last seen mer off the stack
        last = rp.pop()

        # If they don't react, push them onto the stack
        if not is_react_pair(mer, last):
            rp.push(last)
            rp.push(mer)

    return rp

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
    data = ''.join(lines)

# Reduce polymer string
rp = reduce_polymer(data)
print("(a) Length = {:d}".format(rp.size))  # Length = 11636

# OG:
# 52.1 s ± 16.6 s per loop (mean ± std. dev. of 7 runs, 1 loop each)
# Stack:
# 65.4 ms ± 2.28 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

#------------------------------------------------------------------------------ 
#        Part 2
#------------------------------------------------------------------------------
import string 

def remove_units(data, c):
    """Remove all instances of c, case-insensitive, from data."""
    return [x for x in data if ((x != c.lower()) and (x != c.upper()))]

min_len = len(data)
min_chr = -1
for c in string.ascii_lowercase:
    pm = remove_units(data, c)
    rp = reduce_polymer(pm)
    if rp.size < min_len:
        min_len = rp.size
        min_chr = c

print('(b) Remove {}/{}, length = {:d}'\
        .format(min_chr.upper(), min_chr, min_len))


#==============================================================================
#==============================================================================
