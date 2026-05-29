#!/usr/bin/env python3
# ==============================================================================
#     File: indexpq_merge.py
#  Created: 2019-05-22 23:07
#   Author: Bernie Roesler
# ==============================================================================

"""Test for merging streams via an indexed priority queue."""

import sys
from contextlib import ExitStack
from pathlib import Path

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

    # While at least one of the streams has elements left, pop/output the
    # minimum queued value, then get another value from that stream
    while pq:
        i, v = pq.dequeue()
        yield v
        c = streams[i].readline().strip()
        if c:
            pq[i] = c


if __name__ == '__main__':
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        DATA_PATH = Path(__file__).parent.parent / 'data'
        files = sorted(DATA_PATH.glob("m?.txt"))

    with ExitStack() as stack:  # turn into stream read from file
        streams = [stack.enter_context(f.open()) for f in files]
        m = merge(streams)
        print(' '.join(m))


# ==============================================================================
# ==============================================================================
