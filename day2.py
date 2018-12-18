#!/Users/bernardroesler/anaconda3/bin/python3
#==============================================================================
#     File: day2.py
#  Created: 2018-12-16 21:23
#   Author: Bernie Roesler
#
"""
  Description: Find strings with repeated characters
"""
#==============================================================================

filename = "day02.txt"

def hasn(s, n):
    """Determine if string has any characters repeated exactly n times."""
    d = dict()  # store letters seen
    # Populate dictionary with character counts
    for c in s:
        if c in d:
            d[c] += 1
        else:
            d[c] = 1

    # Logic
    if any([v == n for v in d.values()]):
        return 1
    else:
        return 0

#------------------------------------------------------------------------------ 
#        Part 1
#------------------------------------------------------------------------------
has2_tot = 0
has3_tot = 0

with open(filename, 'r') as f:
    for line in f:
        has2_tot += hasn(line, 2)
        has3_tot += hasn(line, 3)

checksum = has2_tot * has3_tot
print(f"Checksum = {checksum:d}")

#------------------------------------------------------------------------------ 
#        Part 2
#------------------------------------------------------------------------------
with open(filename, 'r') as f:
    lines = f.readlines()


#==============================================================================
#==============================================================================
