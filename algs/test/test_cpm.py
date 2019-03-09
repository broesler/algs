#!/usr/bin/env python3
#==============================================================================
#     File: test_cpm.py
#  Created: 2019-03-09 16:34
#   Author: Bernie Roesler
#
"""
  Description: Critical Path Method
"""
#==============================================================================

from algs import Digraph, AcyclicPath

filename = 'test_data/jobsPC.txt'

G = Digraph()
with open(filename, 'r') as file:
    lines = iter(file.readlines())
    V = int(next(lines))
    for i, line in enumerate(lines):
        # duration, n_prec, prec_a, prec_b, ...
        nums = iter(line.rstrip().split())

        duration = float(next(nums))
        G.add_edge('source',   str(i), 0.0)    # source to the start of the job
        G.add_edge(str(i)+'x', 'sink', 0.0)    # end of the job to the sink
        G.add_edge(str(i), str(i)+'x', duration)  # duration of the job

        # Add precedence constraints
        for j in range(int(next(nums))):
            prec = str(next(nums))
            G.add_edge(str(i)+'x', prec, 0.0)

# Find longest path from source to sink
lp = AcyclicPath(G, 'source', kind='max')

print(" job   start  finish")
print("--------------------")
for idx in range(V):
    i = str(idx)
    print(f"{i:>4s} {lp.dist_to(i):7.1f} {lp.dist_to(i+'x'):7.1f}")
print(f"Finish time: {lp.dist_to('sink'):7.1f}")

#==============================================================================
#==============================================================================
