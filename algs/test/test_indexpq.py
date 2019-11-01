#!/usr/bin/env python3
#==============================================================================
#     File: test_indexpq.py
#  Created: 2019-05-22 23:07
#   Author: Bernie Roesler
#
"""
  Description: Test for merging streams via an indexed priority queue.
"""
#==============================================================================

import sys

from algs.basics import IndexPQ


def merge(streams):
    """Merge list of streamed data into single output stream."""
    pq = IndexPQ(kind='min')

    # Create an indexed priority queue with a key for each stream, and read the
    # first item into the queue
    for i, s in enumerate(streams):
        c = s.readline().strip()
        if c:
            pq[i] = c

    # While at least one of the streams has elements left, output the minimum
    # queued value, then get another value from that stream
    while pq:
        i, v = pq.dequeue()
        print(v)  # yield i?
        c = streams[i].readline().strip()
        if c:
            pq[i] = c


if __name__ == '__main__':
    streams = list()
    for a in sys.argv[1:]:
        streams.append(open(a, 'r'))  # turn into stream read from file
    merge(streams)
    for s in streams:
        s.close()


#==============================================================================
#==============================================================================
