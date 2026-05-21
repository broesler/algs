#!/usr/bin/env python3
# =============================================================================
#     File: degrees_of_separation.py
#  Created: 2022-06-16 16:50
#   Author: Bernie Roesler
#
"""
Exercise 4.1.25 Modify DegreesOfSeparation to limit by movie year.
"""
# =============================================================================

import pickle
import re
from pathlib import Path

from algs.graph import BreadthFirstPaths, SymbolGraph

pkl_file = Path('./pkl/movies_SymbolGraph.pkl')

THIS_YEAR = 2011


def degrees_of_separation(sg, source, sink, y=None):
    """Return the shortest path from source to sink in a symbol graph."""
    pat = re.compile(r'\(([0-9]{4})[^)]*\)')
    # See p 555
    if source not in sg:
        raise ValueError(f"{repr(source)} not in graph!")
    s = sg.index(source)

    # Exercise 4.1.25: Filter by recency
    if y is not None:
        G = sg.G.copy()
        # movies are odd vertices
        for v in list(G.vertices()):
            if m := pat.search(sg.name(v)):
                year = int(m.group(1))
                if (THIS_YEAR - year) > y:
                    G._hide_vertex(v)

    bfs = BreadthFirstPaths(G, s)
    if sink in sg:
        print(f"{source}->{sink}")
        t = sg.index(sink)
        if bfs.has_path_to(t):
            for v in bfs.path_to(t):
                print(' ', sg.name(v))
        else:
            print('Not connected.')
    else:
        raise ValueError(f"{repr(sink)} not in graph!")


# sg = SymbolGraph.fromfile(Path('../data/movies.txt'), delim='/')
with open(pkl_file, 'rb') as fp:
    sg = pickle.load(fp)

# Print the shortest path, only including movies < `y` years old.
degrees_of_separation(sg, 'Bacon, Kevin', 'Kidman, Nicole', y=20)

# =============================================================================
# =============================================================================
