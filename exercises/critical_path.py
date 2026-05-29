#!/usr/bin/env python3
# ==============================================================================
#     File: critical_path.py
#  Created: 2019-03-09 16:34
#   Author: Bernie Roesler
# ==============================================================================

r"""Critical Path Method.

Solve the parallel precedence-constrained job scheduling problem via the
*critical path method*. It reduces the problem to the longest-paths problem in
edge-weighted DAGs. It builds an edge-weighted digraph (which must be a DAG)
from the job-scheduling problem specification, finds the longest-paths tree,
and computes the longest-paths lengths (which are precisely the start times for
each job).

This implementation uses :class:`AcyclicPath` to find a longest path in a DAG.
The program takes :math:`\Theta(V + E)` time in the worst case, where *V* is
the number of jobs and *E* is the number of precedence constraints.

For additional documentation, see `Section 4.4
<https://algs4.cs.princeton.edu/44sp>`_ of *Algorithms, 4th Edition*
by Robert Sedgewick and Kevin Wayne.
"""

from pathlib import Path

from algs.graph import AcyclicPath, Digraph

filename = Path(__file__).parent.parent / 'data' / 'jobsPC.txt'

G = Digraph()
with filename.open() as file:
    lines = iter(file.readlines())
    V = int(next(lines))
    for i, line in enumerate(lines):
        # duration, n_prec, [must complete before]
        nums = iter(line.rstrip().split())

        duration = float(next(nums))
        G.add_edge('source', str(i), 0.0)  # source to the start of the job
        G.add_edge(str(i) + 'x', 'sink', 0.0)  # end of the job to the sink
        G.add_edge(str(i), str(i) + 'x', duration)  # duration of the job

        # Add precedence constraints from end of task to start of next task
        for _ in range(int(next(nums))):
            prec = str(next(nums))
            G.add_edge(str(i) + 'x', prec, 0.0)

# Find longest path from source to sink
lp = AcyclicPath(G, 'source', kind='max')
tasks = [str(i) for i in range(V)]
#         job start          finish
output = [(v, lp.dist_to(v), lp.dist_to(v + 'x')) for v in tasks]

print(" job   start  finish")
print("--------------------")
# Sort by start time
for v in sorted(output, key=lambda x: x[1]):
    print("{:>4s} {:7.1f} {:7.1f}".format(*v))
print(f"Finish time: {lp.dist_to('sink'):7.1f}")

assert lp.dist_to('source') == 0.0
assert lp.dist_to('sink') == 173.0

# ==============================================================================
# ==============================================================================
