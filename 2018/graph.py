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
    def __init__(self, name, neighbors=list()):
        self.name = name
        self.neighbors = set(neighbors)
        self.indegree = 0

    def __repr__(self):
        return f'<Node {self.name}:{self.neighbors}>'

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
        List of nodes in `Digraph`.
    """
    def __init__(self, nodes=list()):
        self.nodes = dict()
        if nodes:
            for node in nodes:
                self.nodes[node.name] = node

    def count(self):
        return len(G.nodes)

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
        if a in self.nodes:
            self.nodes[a].neighbors.add(b)
        else:
            self.nodes[a] = Node(a, [b])

        if b in self.nodes:
            self.nodes[b].indegree += 1
        else:
            self.nodes[b] = Node(b, [])

    def get_next(self, node):
        return self.nodes[min(node.neighbors)]  # first alphabetically

    def traverse_graph(self, start=None, path=None):
        """Depth-first search."""
        if not start:
            start = self.find_root()

        if not path:
            path = list()
        
        # Track path through the graph
        path.append(start.name)

        if start.neighbors:
            next_node = self.get_next(start)
            self.traverse_graph(next_node, path)

        return path


#==============================================================================
#==============================================================================
