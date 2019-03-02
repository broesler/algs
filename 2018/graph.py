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

    def __str__(self):
        return str(self.adj).replace('],', ']\n')


class BFSPaths():
    """Breadth-first search class.

    Parameters
    ----------
    G : :obj:`Digraph`
    sources : iterable of vertex ids
        Iterable of vertex ids from which to begin the search.
    ordered : bool, optional
        Traverse the nodes in a specific order, determined by `choose_next`.
    choose_next : callable, optional
        Function that accepts an iterable and returns a single value in
        order to choose an vertex from the available list.

    Attributes
    ----------
    G : :obj:`Digraph`
        The directed graph object to search.
    sources : iterable
        Iterable of given sources, or vertices with indegree 0.
    all_paths : list
        List of all vertices touched during BFS.
    """
    def __init__(self, G, sources=None, ordered=False, choose_next=None):
        if not isinstance(G, Digraph):
            raise Exception('BFS requires a Digraph type.')
        self.G = G
        self.sources = sources or self.G.roots()
        self.all_paths = list()
        self._edge_to = dict()  # v -> w : edge_to[w] = v
        self._visited = dict()
        for v in G:
            self._visited[v] = False
        # populate edge_to dict via the search
        if ordered:
            self.ordered_bfs(choose_next)
        else:
            self._bfs()

    def has_path_to(self, v):
        """has_path_to(v) returns True if there is a path from s -> w.

        Parameters
        ----------
        v : vertex id
            A vertex id, typically int or str.
        """
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
        available = Queue()
        for s in self.sources:
            self._visited[s] = True
            available.enqueue(s)

        while available:
            v = available.dequeue()
            self.all_paths.append(v)
            for w in self.G[v]:
                if not self._visited[w]:
                    self._visited[w] = True
                    self._edge_to[w] = v
                    available.enqueue(w)

    def ordered_bfs(self, choose_next=lambda x: x[0]):
        """Traverse all edges breadth-first.

        Sets self._edge_to, self._visited.

        Parameters
        ----------
        choose_next : callable, optional, default `lambda x: x[0]`
            Function that accepts an iterable and returns a single value in
            order to choose an vertex from the available list. The default is
            to take the first value from the list.

        """
        # TODO store `available` in a min priority queue so we can efficiently
        # get the min value and keep traversing
        available = set(self.sources)

        while available:
            v = choose_next(available)
            self.all_paths.append(v)
            self._visited[v] = True  # unnecessary for this algorithm
            available.remove(v)

            for w in self.G[v]:
                # TODO add custom node attribute to track pre-reqs
                # Generalize: `visit_condition` and `graph_update`
                if self.G.indegree[w] == 1:
                    self._visited[w] = True
                    self._edge_to[w] = v
                    available.add(w)
                self.G.indegree[w] -= 1  # pre-req is done

#------------------------------------------------------------------------------
#        TEST CLIENT
#------------------------------------------------------------------------------
if __name__ == '__main__':
    import re
    def parse(line):
        match = re.search('(\d+)\s+(\d+)', line)
        return int(match.group(1)), int(match.group(2))

    filename = 'test_data/tinyDG.txt'
    # filename = 'test_data/mediumDG.txt'
    G = Digraph()
    with open(filename, 'r') as file:
        for i, line in enumerate(file.readlines()):
            if i < 2: continue
            a, b = parse(line)
            G.add_edge(a, b)

    # Test graph construction
    if filename == 'test_data/tinyDG.txt':
        assert 13 == G.V
        assert 22 == G.E
    elif filename == 'test_data/mediumDG.txt':
        assert 50 == G.V
        assert 147 == G.E

    # Test BFS
    s = G.roots()[0]        # get the first source
    bfs = BFSPaths(G, [s])  # BFS from source(s)

    # Print paths from source to all other nodes
    for v in range(G.V):
        if bfs.has_path_to(v):
            print("{:<2d} to {:2d}:  ".format(s, v), end='')
            for x in bfs.path_to(v):
                if x == s:
                    print(x, end='')
                else:
                    print('-' + str(x), end='')
            print()
        else:
            print("{:<2d} to {:2d}:  not connected".format(s, v))

#==============================================================================
#==============================================================================
