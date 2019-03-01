#!/Users/bernardroesler/anaconda3/envs/insight/bin/python3
#==============================================================================
#     File: graph.py
#  Created: 2019-02-20 22:40
#   Author: Bernie Roesler
#
"""
  Description: Directed graph class
"""
#==============================================================================

class Node():
    """Node of a graph.

    Parameters
    ----------
    name : str
        Name of the node
    neighbors : iterable of str, optional
        Iterable of the node names to which this node is connected.

    Attributes
    ----------
    name : str
        Name of the node
    neighbors : iterable of str
        Iterable of the node names to which this node is connected.
    indegree : int
        Number of nodes pointing to this node.
    """
    def __init__(self, node_id, children=list()):
        self.id = node_id
        self.next = set(children)
        self.indegree = 0
        self.visited = False

    def add_next(self, b):
        self.next.add(b)

    def __repr__(self):
        return f'<Node {self.id}:{self.next}>'

class Digraph():
    """Directed graph represented as a dictionary of Nodes.
    
    Parameters
    ----------
    nodes : :obj:`list` of :obj:`Node`
        List of nodes to initialize the directed `Digraph`. The first node will
        be marked as the start of the Digraph. The order of the following nodes
        does not matter.

    Attributes
    ----------
    nodes : :obj:`list` of :obj:`Node`
        List of nodes in `Digraph`. Includes those added with `Digraph.add_node`.
    root : :obj:`Node`
        Starting node from which all others stem.

    """
    def __init__(self, nodes=list()):
        self.nodes = dict()
        if nodes:
            for node in nodes:
                self.nodes[node.id] = node
        self.E = 0

    @property
    def V(self):
        return len(self.nodes)

    def find_all_roots(self):
        """List of nodes with indegree zero."""
        return [x for x, y in self.nodes.items() if y.indegree == 0]

    def find_root(self):
        """Find node with indegree 0."""
        pass

    def add_edge(self, a, b):
        """Add edge between two node names.

        Parameters
        ----------
        a : str
            Starting node name
        b : str
            Ending node name
        """
        self.E += 1

        if a in self.nodes:
            self.nodes[a].add_next(b)
        else:
            self.nodes[a] = Node(a, [b])

        if b not in self.nodes:
            self.nodes[b] = Node(b, [])
        self.nodes[b].indegree += 1

    def bfs_all(self, available=None, path=None):
        """Traverse all nodes breadth-first. Choose lowest alphabetical.

        Parameters
        ----------
        available : :obj:`list`
            List of node ids to which we can travel next.
        path : :obj:`list`
            List of node ids to which we have already traveled.

        Returns
        -------
        path : :obj:`list`
            List of node ids to which we have already traveled.
        """
        if not available:
            # TODO store "available" in a priority queue so we can efficiently
            # get the min value and keep traversing
            available = set(self.find_all_roots())
        if not path:
            path = list()

        curr = self.nodes[min(available)]  # first alphabetically
        path.append(curr.id)
        available.remove(curr.id)
        curr.visited = True

        if curr.next:
            children = list()
            for n in curr.next:
                if not self.nodes[n].visited and self.nodes[n].indegree < 2:
                    children.append(self.nodes[n].id)
                self.nodes[n].indegree -= 1  # pre-req is done for children
            available.update(children)

        if available:
            self.bfs_all(available, path)

        return path






#==============================================================================
#==============================================================================
