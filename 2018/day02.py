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

#------------------------------------------------------------------------------ 
#        Part 1
#------------------------------------------------------------------------------
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

# Main loop
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
def idx_diff(s1, s2):
    """Return indices where strings differ."""
    return [i for i in range(len(s1)) if s1[i] != s2[i]]

# Read lines from file
with open(filename, 'r') as f:
    lines = [x.rstrip() for x in f.readlines()]

# Find 2 strings that differ by only one character in the same location
# NOTE SLOW!! Could maybe sort this list first?
for i, s1 in enumerate(lines):
    for j in range(i+1, len(lines)):
        s2 = lines[j]
        idx = idx_diff(s1, s2)
        if len(idx) == 1:
            # Return similar characters
            out = s1[:idx[0]] + s1[idx[0]+1:]
            break
    else:
        # If inner loop didn't break
        continue
    # If inner loop breaks
    break

print(f"Common chars = '{out}'")

#==============================================================================
#==============================================================================
