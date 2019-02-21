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
    def __init__(self, name, neighbors=list()):
        self.name = name
        self.neighbors = neighbors

    def __repr__(self):
        return f'<Node {self.name}:{self.neighbors}>'

class Graph():
    """Directed graph represented as a dictionary of Nodes.
    
    Parameters
    ----------
    nodes : :obj:`list` of :obj:`Node`
        List of nodes to initialize the directed `Graph`. The first node will
        be marked as the start of the Graph. The order of the following nodes
        does not matter.

    Attributes
    ----------
    nodes : :obj:`list` of :obj:`Node`
        List of nodes in `Graph`. Includes those added with `Graph.add_node`.
    root : :obj:`Node`
        Starting node from which all others stem.

    """
    def __init__(self, nodes=list()):
        self.nodes = dict()
        self.root = None
        if nodes:
            self.root = nodes[0]
            for node in nodes:
                self.nodes[node.name] = node

    def count(self):
        return len(G.nodes)

    def add_edge(self, a, b):
        """Add edge between two node names.

        Parameters
        ----------
        a, b : char
            Node names
        """
        self.add_node(Node(a, [b]))
        self.add_node(Node(b, []))

    def add_node(self, new_node):
        """Update existing node, or create new one.

        Parameters
        ----------
        new_node : :obj:`Node`
            Node object to be added to graph.
        """
        if not self.nodes:
            self.root = new_node
        if new_node.name in self.nodes:
            self.nodes[new_node.name].neighbors.extend(new_node.neighbors)
        else:
            self.nodes[new_node.name] = new_node

    def get_next(self, node):
        return self.nodes[min(node.neighbors)]  # first alphabetically

    def traverse_graph(self, start=None, path=None):
        """Depth-first search."""
        if not start:
            start = self.root

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
