#!/Users/bernardroesler/anaconda3/envs/insight/bin/python3
#==============================================================================
#     File: day07.py
#  Created: 2019-02-20 22:31
#   Author: Bernie Roesler
#
"""
  Description: --- Day 7: The Sum of Its Parts ---
"""
#==============================================================================

import re
import graph

pat = re.compile('Step (\w) must be finished before step (\w) can begin\.')

def should_be(a, b):
    """Comparison function for testing."""
    if a != b:
        raise Exception(f'Got {a}, expected {b}')

def parse(line):
    """Parse line from data file to get two characters."""
    match = pat.match(line)
    return match.group(1).upper(), match.group(2).upper()

#------------------------------------------------------------------------------ 
#        Main
#------------------------------------------------------------------------------
# filename = 'data/test_input07.dat'
filename = 'data/input07.dat'

G = graph.Digraph()

with open(filename, 'r') as file:
    for line in file.readlines():
        a, b = parse(line)
        G.add_edge(a, b)

# Need to do BREADTH-FIRST search!
path = G.bfs_all()
print(''.join(path))
should_be(len(path), G.V)  # all vertices visited

#==============================================================================
#==============================================================================
