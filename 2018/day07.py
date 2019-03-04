#!/usr/bin/env python3
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

from basics.stack import Stack
from basics.queue import Queue
from basics.priority_queue import PriorityQueue

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
filename = 'test_data/test_input07.dat'
# filename = 'data/input07.dat'

G = graph.Digraph()

with open(filename, 'r') as file:
    for line in file.readlines():
        a, b = parse(line)
        G.add_edge(a, b)

# choose first alphabetical node to operate on first
bfs = graph.BFSPaths(G, ordered=True)
path = ''.join(bfs.all_paths)
print(path)
should_be(len(path), G.V)  # all vertices visited

if filename == 'test_data/test_input07.dat':
    should_be(path, 'CABDFE')
elif filename == 'data/input07.dat':
    should_be(path, 'GNJOCHKSWTFMXLYDZABIREPVUQ')

#------------------------------------------------------------------------------ 
#        Part 2
#------------------------------------------------------------------------------
# Second   Worker 1   Worker 2   Done
#    0        C          .        
#    1        C          .        
#    2        C          .        
#    3        A          F       C
#    4        B          F       CA
#    5        B          F       CA
#    6        D          F       CAB
#    7        D          F       CAB
#    8        D          F       CAB
#    9        D          .       CABF
#   10        E          .       CABFD
#   11        E          .       CABFD
#   12        E          .       CABFD
#   13        E          .       CABFD
#   14        E          .       CABFD
#   15        .          .       CABFDE

# Like BFS, but need to "wait" at each vertex. PriorityQueue tasks as they
# become available, and pass to workers who are free.
# Weighted edge graph where each edge has the weight of the originating node
# Find maximum path?
# BFS, but update the weights each time a node is visited.

task_cost = lambda v: ord(v) - ord('A') + 1  # 'A' = 1, 'B' = 2, etc.

task_time = dict({v : task_cost(v)  for v in G.vertices()})
# task_time = dict({v : 60 + task_cost(v) for v in G.vertices()})
Nw = 2  # number of workers

tot_time = 0

class Worker():
    def __init__(self, task='A', time=0):
        self.task = task
        self.time = time
    def __repr__(self):
        return f'<Worker: {self.task}:{self.time}>'

prereqs = G.indegree.copy()  # mutable copy
workers = list()
done = dict()
for v in G:
    done[v] = False
available = PriorityQueue(G.roots(), kind='min')

while available:
    while available and len(workers) < Nw:
        v = available.dequeue()
        workers.append(Worker(v, task_time[v]))

    # "advance" time the maximum possible
    #{
    min_time = (min(workers, key=lambda x: x.time)).time
    tot_time += min_time

    done_tasks = list()
    for w in workers:
        w.time -= min_time
        if w.time == 0:
            done_tasks.append(w)

    for x in done_tasks:
        workers.remove(x) 
        done[x] = True
    #}

    for w in G[v]:
        if prereqs[w] == 1:
            available.enqueue(w)
        if done[v]:
            prereqs[w] -=1

print(tot_time)


#==============================================================================
#==============================================================================
