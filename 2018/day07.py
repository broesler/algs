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

def parse(line):
    match = pat.match(line)
    return match.group(1).upper(), match.group(2).upper()

filename = 'data/input07.dat'

G = graph.Graph()

with open(filename, 'r') as file:
    data = list()
    for line in file.readlines():
        a, b = parse(line)
        data.append((a, b))
        G.add_edge(a, b)

path = G.traverse_graph(G.nodes['M'])
print(''.join(path))

#==============================================================================
#==============================================================================
