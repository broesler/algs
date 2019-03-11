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
        # duration, n_prec, [must complete before]
        nums = iter(line.rstrip().split())

        duration = float(next(nums))
        G.add_edge('source',       str(i), 0.0)    # source to the start of the job
        G.add_edge(str(i)+'x',     'sink', 0.0)    # end of the job to the sink
        G.add_edge(str(i),     str(i)+'x', duration)  # duration of the job

        # Add precedence constraints from end of task to start of next task
        for j in range(int(next(nums))):
            prec = str(next(nums))
            G.add_edge(str(i)+'x', prec, 0.0)

# Find longest path from source to sink
lp = AcyclicPath(G, 'source', kind='max')
tasks = [str(i) for i in range(V)]
#         job start          finish
output = [(v, lp.dist_to(v), lp.dist_to(v+'x')) for v in tasks]

print(" job   start  finish")
print("--------------------")
# Sort by start time
for v in sorted(output, key=lambda x: x[1]):
    print("{:>4s} {:7.1f} {:7.1f}".format(*v))
print(f"Finish time: {lp.dist_to('sink'):7.1f}")

assert lp.dist_to('source') == 0.0
assert lp.dist_to('sink') == 173.0

#==============================================================================
#==============================================================================
