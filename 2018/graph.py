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
        self.neighbors = set(neighbors)
        self.indegree = 0

    def add_neighbor(self, b):
        self.neighbors.add(b)

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
        if nodes:
            for node in nodes:
                self.nodes[node.name] = node
        self.E = 0

    @property
    def V(self):
        return len(self.nodes)

    def find_root(self):
        return [x for x, y in self.nodes.items() if y.indegree == 0]

    def add_edge(self, a, b):
        """Add edge between two node names.

        Parameters
        ----------
        a, b : char
            Node names
        """
        self.E += 1

        if a in self.nodes:
            self.nodes[a].add_neighbor(b)
        else:
            self.nodes[a] = Node(a, [b])

        if b not in self.nodes:
            self.nodes[b] = Node(b, [])
        self.nodes[b].indegree += 1

    def get_next(self, a):
        """Get the next node to traverse."""
        try:
            node = self.nodes[a]
            return self.nodes[min(node.neighbors)]  # first alphabetically
        except (KeyError, ValueError):
            return None

    def traverse_graph(self, start=None, path=None):
        """Depth-first search."""
        if not start:
            start = self.find_root()[0]

        if not path:
            path = list()
        
        # Track path through the graph
        path.append(start)

        next_node = self.get_next(start)
        if next_node:
            self.traverse_graph(next_node.name, path)

        return path


#==============================================================================
#==============================================================================
