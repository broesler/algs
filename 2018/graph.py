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
    outdegree : int
        Number of vertices to which this vertex points.
    """
    def __init__(self, vertex_id, adjacent=list()):
        self.id = vertex_id
        self.adj = set(adjacent)
        self.indegree = 0
        self.visited = False

    @property
    def outdegree(self):
        """Number of vertices to which this vertex points."""
        return len(self.adj)

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
        for vertex in vertices:
            self._vertices[vertex.id] = vertex
        self.E = 0

    @property
    def V(self):
        return len(self._vertices)

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

    Attributes
    ----------
    G : :obj:`Digraph`
        The directed graph object to search.
    """
    def __init__(self, G, sources=None):
        if not isinstance(G, Digraph):
            raise Exception('BFS requires a Digraph type.')
        self.G = G
        self.edge_to = dict()  # v -> w : edge_to[w] = v
        self.dist_to = dict()  # distance from source to 
        for v in G:
            self.dist_to[v] = INT_MAX
        self.bfs(sources)      # populate edge_to dict

    def find_all_roots(self):
        """List of vertices with indegree zero."""
        return [n.id for n in self.G if n.indegree == 0]

    def has_path_to(self, v):
        """has_path_to(v) is True if there is a path from s -> w."""
        return self.G[v].visited

    def path_to(self, v):
        """Returns path from source vertex to v."""
        if not self.has_path_to(v):
            return None

        path = Stack()
        x = v
        while self.dist_to[x]:
            path.push(x)
            x = self.edge_to[x]
        path.push(x)
        return path
        

    def bfs(self, sources=None):
        """Traverse all vertices breadth-first.

        Parameters
        ----------
        sources : iterable of `Vertex` ids
            Iterable of vertex ids from which to begin the search.

        Returns
        -------
        path : :obj:`list`
            List of vertex ids to which we have already traveled.
        """
        if not sources:
            sources = self.find_all_roots()

        available = Queue()
        for s in sources:
            self.G[s].visited = True
            self.dist_to[s] = 0
            available.enqueue(s)

        while available:
            v = self.G[available.dequeue()]
            for a in v.adj:
                w = self.G[a]
                if not w.visited:
                    w.visited = True
                    self.edge_to[w.id] = v.id
                    self.dist_to[w.id] = self.dist_to[v.id] + 1
                    available.enqueue(w.id)

    # def ordered_bfs(self, sources=None):
    #     """Traverse all edges breadth-first. Choose minimum vertex_id first.
    #
    #     Parameters
    #     ----------
    #     sources : iterable of `Vertex` ids
    #         Iterable of vertex ids from which to begin the search.
    #
    #     Returns
    #     -------
    #     path : :obj:`list`
    #         List of vertex ids to which we have traveled, in order.
    #     """
    #     path = list()
    #     if not sources:
    #         sources = self.find_all_roots()
    #
    #     # TODO store `available` in a min priority queue so we can efficiently
    #     # get the min value and keep traversing
    #     available = set(sources)
    #
    #     while available:
    #         curr = self.G[min(available)]
    #         path.append(curr.id)
    #         curr.visited = True
    #         available.remove(curr.id)
    #
    #         if curr.adj:
    #             for vertex_id in curr.adj:
    #                 n = self.G[vertex_id]
    #                 if not n.visited and n.indegree < 2:
    #                     available.add(n.id)
    #                 n.indegree -= 1  # pre-req is done
    #
    #     return path

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

    bfs = BFSPaths(G)
    s = bfs.find_all_roots()[0]  # take the first (only one for example

    # Print paths from source to all other nodes
    for v in range(G.V):
        if bfs.has_path_to(v):
            print("{:<2d} to {:2d} ({:d}):  ".format(s, v, bfs.dist_to[v]), end='')
            for x in bfs.path_to(v):
                if x == s:
                    print(x, end='')
                else:
                    print('->' + str(x), end='')
            print()
        else:
            print("{:<2d} to {:2d} (-):  not connected".format(s, v))



#==============================================================================
#==============================================================================
