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

def flatten(forest): 
    """Flatten all elements of all sublists into one single list."""
    return [leaf for tree in forest for leaf in tree]

def parse(line):
    match = pat.match(line)
    return match.group(1).upper(), match.group(2).upper()

def should_be(a, b):
    if a != b:
        raise Exception(f'Got {a}, expected {b}')

filename = 'data/input07.dat'

G = graph.Graph()

with open(filename, 'r') as file:
    data = list()
    for line in file.readlines():
        a, b = parse(line)
        data.append((a, b))
        G.add_edge(a, b)

# Test graph building
f = flatten(data)
V = len(set(f))
E = len(f) / 2
should_be(E % 1, 0)
should_be(G.V, V)
should_be(G.E, E)

path = G.traverse_graph()
print(''.join(path))

#==============================================================================
#==============================================================================
