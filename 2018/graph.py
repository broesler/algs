#!/usr/bin/env python3
#==============================================================================
#     File: graph.py
#  Created: 2019-02-20 22:40
#   Author: Bernie Roesler
#
"""
  Description: Directed graph and supporting classes
"""
#==============================================================================

from basics.stack import Stack
from basics.queue import Queue
from basics.priority_queue import PriorityQueue

class Digraph():
    """Directed graph represented as a dictionary of Vertices.

    Parameters
    ----------
    vertices : iterable of vertex ids
        Iterable of vertices to initialize the directed `Digraph`.

        *NOTE*: Vertices are stored as a dictionary, so duplicate ids in the
        list will overwrite.

    Attributes
    ----------
    V : int
        Number of vertices in the graph.
    E : int
        Number of edges in the graph.
    adj : dict of lists of vertices
        `adj[v]` returns adjacency list of vertices to which `v` points.
    indegree : dict of int
        `indegree[v]` is number of vertices that have edges to `v`.
    """
    def __init__(self, vertices=list()):
        self.E = 0
        self.V = 0
        self.adj = dict()       # vertex adjacency list
        self.indegree = dict()  # list of vertex indegrees
        for v in vertices:
            self._init_vertex(v)

    def roots(self):
        """List of vertices with indegree zero."""
        return [v for v in self if self.indegree[v] == 0]

    def vertices(self):
        return set(self.adj.keys()) #and set(self.indegree.keys())

    def add_edge(self, a, b):
        """Add edge between two vertex ids.

        Parameters
        ----------
        a : str or int
            Starting vertex id
        b : str or int
            Ending vertex id
        """
        self.E += 1

        if a in self.adj:
            self.adj[a].append(b)
        else:
            self._init_vertex(a, [b])

        if b not in self.indegree:
            self._init_vertex(b)
        self.indegree[b] += 1

    def _init_vertex(self, v, w=list()):
        """Add a new vertex to the graph.

        Parameters
        ----------
        v : vertex id (str or int)
            Name of vertex to add to the graph
        w : list of vertex ids
            Adjacent vertices to `v`. May be empty.
        """
        self.V += 1
        self.adj[v] = list(w)
        self.indegree[v] = 0

    def __getitem__(self, v):
        return self.adj[v]

    def __iter__(self):
        yield from self.vertices()

    def __repr__(self):
        return str(self.adj).replace('],', ']\n')

    def __str__(self):
        return self.__repr__()


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
        #       * only allow a single source
        #           - would require special logic to do _unordered_bfs on all
        #           sources for day07.py
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

#------------------------------------------------------------------------------
#        TEST CLIENT
#------------------------------------------------------------------------------
if __name__ == '__main__':
    import re
    pat = re.compile('(\d+)\s+(\d+)')
    def parse(line):
        match = pat.search(line)
        return int(match.group(1)), int(match.group(2))

    # Load test file
    # filename = 'test_data/tinyDG.txt'
    filename = 'test_data/tinyDAG.txt'
    # filename = 'test_data/mediumDG.txt'

    G = Digraph()
    with open(filename, 'r') as file:
        for i, line in enumerate(file.readlines()):
            if i < 2: continue
            a, b = parse(line)
            G.add_edge(a, b)

    # Test BFS
    s = G.roots()[0]  # get the first source
    bfs = BFSPaths(G, [s])
    print('Unordered BFS:')
    print('--------------')
    bfs.print_paths()

    # Test Ordered BFS
    bfs_o = BFSPaths(G, [s], ordered=True)
    print('Ordered BFS:')
    print('------------')
    bfs_o.print_paths()

#==============================================================================
#==============================================================================
