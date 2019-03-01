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

from basics.queue import Queue

class Node():
    """Node of a graph.

    Parameters
    ----------
    node_id : str
        id of the node
    next_available : iterable of str, optional
        Iterable of the node names to which this node is connected.

    Attributes
    ----------
    id : str
        id of the node
    next : iterable of str
        Iterable of the node names to which this node is connected.
    indegree : int
        Number of nodes pointing to this node.
    outdegree : int
        Number of nodes to which this node points.
    """
    def __init__(self, node_id, next_available=list()):
        self.id = node_id
        self.next = set(next_available)
        self.indegree = 0
        self.visited = False

    @property
    def outdegree(self):
        """Number of nodes to which this node points."""
        return len(self.next)

    def add_next(self, b):
        """Add a node to the list of next_available."""
        self.next.add(b)

    def __repr__(self):
        return f'<Node {self.id}:{self.next}>'


class Digraph():
    """Directed graph represented as a dictionary of Nodes.
    
    Parameters
    ----------
    nodes : iterable of :obj:`Node`
        Iterable of nodes to initialize the directed `Digraph`, with no edges.

        *NOTE*: Nodes are stored as a dictionary, so duplicate `node.id`s in
        the list will overwrite.

    Attributes
    ----------
    V : int
        Number of vertices in the graph.
    E : int
        Number of edges in the graph.
    """
    def __init__(self, nodes=list()):
        # TODO update to allow list of tuples of node ids to create edges.
        self._nodes = dict()
        for node in nodes:
            self._nodes[node.id] = node
        self.E = 0

    @property
    def V(self):
        return len(self._nodes)

    def nodes(self):
        return self._nodes.values()

    def add_edge(self, a, b):
        """Add edge between two node ids.

        Parameters
        ----------
        a : str or int
            Starting node id
        b : str or int
            Ending node id
        """
        self.E += 1

        if a in self._nodes:
            self._nodes[a].add_next(b)
        else:
            self._nodes[a] = Node(a, [b])

        if b not in self._nodes:
            self._nodes[b] = Node(b, [])
        self._nodes[b].indegree += 1

    def __getitem__(self, node_id):
        return self._nodes[node_id]

    def __iter__(self):
        for node in self._nodes.values():
            yield node

    def __str__(self):
        return '\n'.join(str(n) for n in self)



class BFSPaths():
    """Breadth-first search class.

    Parameters
    ----------
    G : :obj:`Digraph`

    Attributes
    ----------
    G : :obj:`Digraph`
        The directed graph object to search.
    all_paths : list
        List of node ids to traverse all nodes in accessible order.
    """
    def __init__(self, G):
        if type(G) is not Digraph:
            raise Exception('BFS requires a Digraph type.')
        self.G = G
        # TODO store paths as edge_to array, v -> w : edge_to[w] = v
        # self.all_paths becomes loop over edge_to[edge_to[...]]
        self.all_paths = list()
        self.bfs_all()

    def find_all_roots(self):
        """Set of nodes with indegree zero."""
        return [n.id for n in self.G if n.indegree == 0]

    def get_next_id(available):
        return available.dequeue()

    def bfs_all(self):
        """Traverse all nodes breadth-first. Choose lowest alphabetical.

        Returns
        -------
        path : :obj:`list`
            List of node ids to which we have already traveled.
        """
        # TODO store `available` in a min priority queue so we can efficiently
        # get the min value and keep traversing
        available = Queue(self.find_all_roots())

        while available:
            curr_id = self.get_next_id(available)
            curr = self.G[curr_id]  # no order in queue
            self.all_paths.append(curr.id)
            curr.visited = True

            if curr.next:
                next_available = list()
                for node_id in curr.next:
                    n = self.G[node_id]
                    if not n.visited and n.indegree < 2:
                        next_available.append(node_id)
                    n.indegree -= 1  # pre-req is done
                available.enqueue(next_available)






#==============================================================================
#==============================================================================
