#!/usr/bin/env python3
#==============================================================================
#     File: search.py
#  Created: 2019-03-03 23:09
#   Author: Bernie Roesler
#
"""
  Description: Graph searching classes.
"""
#==============================================================================

from basics.stack import Stack
from basics.queue import Queue
from basics.priority_queue import PriorityQueue

# NOTE indegree is the only reference to Digraphs, specifically.
class BFSPaths():
    """Breadth-first search class.

    Parameters
    ----------
    G : :obj:`Digraph`
    sources : iterable of vertex ids
        Iterable of vertex ids from which to begin the search.
    ordered : bool, optional
        Traverse the nodes in a specific order.
    kind : str in {'min, 'max'}, optional, default='min'
        How to choose the next node to traverse when outdegree > 1.

    Attributes
    ----------
    G : :obj:`Digraph`
        The directed graph object to search.
    sources : iterable
        Iterable of given sources, or vertices with indegree 0.
    all_paths : list
        List of all vertices touched during BFS.
    """
    def __init__(self, G, sources=None, ordered=False, kind='min'):
        self.G = G
        self.sources = sources or self.G.roots()
        self.all_paths = list()
        self._edge_to = dict()  # v -> w : edge_to[w] = v
        self._visited = dict()
        for v in G:
            self._visited[v] = False
        # populate edge_to dict via the search
        if ordered:
            self._ordered_bfs(kind)
        else:
            self._bfs()

    def has_path_to(self, v):
        """has_path_to(v) returns True if there is a path from *any* s -> w.

        Parameters
        ----------
        v : vertex id
            A vertex id, typically int or str.
        """
        # FIXME only works for *any* source, not a specific source...
        #   fixes:
        #     * only allow a single source
        #         - would require special logic to do _unordered_bfs on all
        #         sources for day07.py
        #     * run DFS from s to determine if there is a path
        return self._visited[v]

    def path_to(self, v):
        """Returns path from source vertex to v.

        Parameters
        ----------
        v : vertex id
            A vertex id, typically int or str.

        Returns
        -------
        path : Stack of keys
            Stack of vertex ids in order of traversal.
        """
        if not self.has_path_to(v):
            return None
        path = Stack()
        x = v
        while x not in self.sources:
            path.push(x)
            x = self._edge_to[x]
        path.push(x)
        return path

    def _bfs(self):
        """Traverse all vertices breadth-first.

        Sets self._edge_to, self._visited.
        """
        available = Queue(self.sources)

        while available:
            v = available.dequeue()
            self.all_paths.append(v)
            self._visited[v] = True

            for w in self.G[v]:
                if not self._visited[w]:
                    self._visited[w] = True
                    self._edge_to[w] = v
                    available.enqueue(w)

    def _ordered_bfs(self, kind):
        """Traverse graph breadth-first, choosing minimum node id first.

        *NOTE* will only find a complete path for a connected, acyclic graph.
        Sets self._edge_to, self._visited.
        """
        prereqs = self.G.indegree.copy()  # mutable copy
        available = PriorityQueue(self.sources, kind='min')

        while available:
            v = available.dequeue()  # take min value
            self.all_paths.append(v)
            self._visited[v] = True

            for w in self.G[v]:
                if prereqs[w] == 1:
                    self._visited[w] = True
                    self._edge_to[w] = v
                    available.enqueue(w)
                prereqs[w] -= 1

    def print_paths(self):
        """Print paths from each source to each other node."""
        for s in self.sources:
            for v in range(self.G.V):
                if self.has_path_to(v):
                    print("{:<2d} -> {:2d}:  ".format(s, v), end='')
                    for x in self.path_to(v):
                        if x == s:
                            print(x, end='')
                        else:
                            print('-' + str(x), end='')
                    print()
                else:
                    print("{:<2d} -> {:2d}:  not connected".format(s, v))

#==============================================================================
#==============================================================================
