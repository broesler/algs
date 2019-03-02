#!/Users/bernardroesler/anaconda3/envs/insight/bin/python3
#==============================================================================
#     File: graph.py
#  Created: 2019-02-20 22:40
#   Author: Bernie Roesler
#
"""
  Description: Directed graph and supporting classes
"""
#==============================================================================

import sys
from basics.stack import Stack
from basics.queue import Queue

INT_MAX = sys.maxsize

class Vertex():
    """Vertex of a graph.

    Parameters
    ----------
    vertex_id : str
        id of the vertex
    adjacent : iterable of str, optional
        Iterable of the vertex names to which this vertex is connected.

    Attributes
    ----------
    id : str or int
        id of the vertex
    adj : iterable
        Iterable of the vertex names to which this vertex is connected.
    indegree : int
        Number of vertices pointing to this vertex.
    """
    def __init__(self, vertex_id, adjacent=list()):
        self.id = vertex_id
        self.adj = set(adjacent)
        self.indegree = 0

    def add_adj(self, b):
        """Add a vertex to the list of adjacent."""
        self.adj.add(b)

    def __repr__(self):
        return f'<Vertex {self.id}:{self.adj}>'


class Digraph():
    """Directed graph represented as a dictionary of Vertices.
    
    Parameters
    ----------
    vertices : iterable of :obj:`Vertex`
        Iterable of vertices to initialize the directed `Digraph`.

        *NOTE*: Vertices are stored as a dictionary, so duplicate `vertex.id`s
        in the list will overwrite.

    Attributes
    ----------
    V : int
        Number of vertices in the graph.
    E : int
        Number of edges in the graph.
    """
    def __init__(self, vertices=list()):
        self._vertices = dict()
        # TODO get rid of Vertex class...
        self._indegree = dict()
        for vertex in vertices:
            self._vertices[vertex.id] = vertex
        self.E = 0

    @property
    def V(self):
        return len(self._vertices)

    def roots(self):
        """List of vertices with indegree zero."""
        return [n.id for n in self if n.indegree == 0]

    def vertices(self):
        return self._vertices.values()

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

        if a in self._vertices:
            self._vertices[a].add_adj(b)
        else:
            self._vertices[a] = Vertex(a, [b])

        if b not in self._vertices:
            self._vertices[b] = Vertex(b, [])

        self._vertices[b].indegree += 1

    def __getitem__(self, vertex_id):
        return self._vertices[vertex_id]

    def __iter__(self):
        yield from self.vertices()

    def __str__(self):
        return '\n'.join(str(n) for n in self)


class BFSPaths():
    """Breadth-first search class.

    Parameters
    ----------
    G : :obj:`Digraph`
    sources : iterable of `Vertex` ids
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
    def __init__(self, G, sources=None,
                 ordered=False, choose_next=lambda x: x[0]):
        if not isinstance(G, Digraph):
            raise Exception('BFS requires a Digraph type.')
        self.G = G
        self.sources = sources or self.G.roots()
        self._edge_to = dict()  # v -> w : edge_to[w] = v
        self._visited = dict()
        for v in G:
            self._visited[v.id] = False
        self.all_paths = list()
        # populate edge_to dict via the search
        if ordered:
            self.ordered_bfs(choose_next)
        else:
            self._bfs()

    def has_path_to(self, v):
        """has_path_to(v) is True if there is a path from s -> w."""
        return self._visited[v]

    def path_to(self, v):
        """Returns path from source vertex to v."""
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
        """Traverse all vertices breadth-first."""
        available = Queue()
        for s in self.sources:
            # self._visited[s] = True
            available.enqueue(s)

        # TODO remove all `*.id` when we destroy Vertex class.
        while available:
            v = self.G[available.dequeue()]
            self.all_paths.append(v.id)
            for a in v.adj:
                w = self.G[a]
                if not self._visited[w.id]:
                    self._visited[w.id] = True
                    self._edge_to[w.id] = v.id
                    available.enqueue(w.id)

    def ordered_bfs(self, choose_next):
        """Traverse all edges breadth-first.

        Parameters
        ----------
        choose_next : callable, optional
            Function that accepts an iterable and returns a single value in
            order to choose an vertex from the available list.

        Returns
        -------
        path : :obj:`list`
            List of vertex ids to which we have traveled, in order.
        """
        # TODO store `available` in a min priority queue so we can efficiently
        # get the min value and keep traversing
        available = set(self.sources)

        while available:
            v = self.G[choose_next(available)]
            self.all_paths.append(v.id)
            self._visited[v.id] = True  # unnecessary for this algorithm
            available.remove(v.id)

            for w_id in v.adj:
                w = self.G[w_id]
                if w.indegree < 2:
                    self._visited[w.id] = True
                    self._edge_to[w.id] = v.id
                    available.add(w.id)
                w.indegree -= 1  # pre-req is done

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
