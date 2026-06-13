#!/usr/bin/env python3
# =============================================================================
#     File: graph_util.py
#  Created: 2026-06-12 21:54
#   Author: Bernie Roesler
# =============================================================================

"""Client functions for use with graph implementations."""

from algs.graph.search import BreadthFirstSearch, DepthFirstSearch
from algs.graph.undirected import CC


# See p 523.
def print_dfs(G, s, DFS=DepthFirstSearch):
    """Search the graph from vertex `s`."""
    # See p 529
    search = DFS(G, s)
    print(" ".join(str(v) for v in G.vertices() if search.has_path_to(v)))
    print(f"{'NOT ' if search.count != G.V else ''}connected.")
    return search


def print_paths(G, s, GS=DepthFirstSearch):
    """Search the graph from vertex `s`, returning the paths."""
    # See p 535
    search = GS(G, s)
    lines = []
    for v in G.vertices():
        prefix = f"{s:2d}->{v:2d}: "
        if search.has_path_to(v):
            path_str = "-".join(str(x) for x in search.path_to(v))
            lines.append(f"{prefix}{path_str}")
        else:
            lines.append(f"{prefix}not connected")
    print("\n".join(lines))


def print_components(G, vertices=None):
    """Compute the connected components in the graph.

    Parameters
    ----------
    G : :obj:`Graph`
        The graph to analyze.
    vertices : iterable, optional
        An iterable of the vertices to consider. If not given, all vertices
        in `G` will be used.

    Returns
    -------
    components : list of lists
        List of lists of the vertices in each connected component.
    """
    # See p 543
    vertices = vertices or G.vertices()
    cc = CC(G, vertices)
    M = cc.count()
    print(f"{M} components")
    components = cc.get_components()
    lines = [f"{i}: {' '.join(str(v) for v in c)}" for i, c in enumerate(components)]
    print("\n".join(lines))
    return components


def print_adj(sg, s):
    """Print the adjacency list of the source."""
    # See p 550
    print(f"{s}: {' '.join(w for w in sg.adj(s))}")


def degrees_of_separation(sg, source, sink):
    """Return the shortest path from source to sink in a symbol graph."""
    # See p 555
    if source not in sg:
        raise ValueError(f"{repr(source)} not in graph!")
    s = sg.index(source)
    bfs = BreadthFirstSearch(sg.G, s)
    if sink in sg:
        print(f"{source}->{sink}")
        t = sg.index(sink)
        if bfs.has_path_to(t):
            print('\n'.join(sg.name(v) for v in bfs.path_to(t)))
        else:
            print('Not connected.')
    else:
        raise ValueError(f"{repr(sink)} not in graph!")


# =============================================================================
# =============================================================================
