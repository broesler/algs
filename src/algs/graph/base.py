#!/usr/bin/env python3
# =============================================================================
#     File: base.py
#  Created: 2026-06-12 11:55
#   Author: Bernie Roesler
# =============================================================================

"""Abstract base classes for graph implementations."""

from abc import ABC, abstractmethod
from pathlib import Path

from tqdm import tqdm

from algs.basics import Bag


class BaseGraph(ABC):
    _RAW_TEMPLATE = """{descr}

    Parameters
    ----------
    {v_descr}
    edges : iterable of 2-tuples
        An iterable of tuples of vertices representing edges.
    parallel : bool, optional
        If True, allow parallel edges.
    self_loops : bool, optional
        If True, allow self-loops.
    """

    _DOC_TEMPLATE = _RAW_TEMPLATE.format(
        descr="{descr}",
        v_descr="""V : int
        The number of vertices in the graph.""",
    )

    __doc__ = _DOC_TEMPLATE.format(
        descr="""An abstract base class implementing the Graph API.

        *See*: Sedgewick and Wayne, *Algorithms*, 4ed, p 522.
        """
    )

    def __init__(self, V=0, edges=None, parallel=True, self_loops=True):
        self._V = V
        self._E = 0
        self._parallel = bool(parallel)
        self._self_loops = bool(self_loops)
        self._adj = self._create_adjacency_structure(V)

        if edges is None:
            edges = []

        try:
            for v, w in edges:
                self.add_edge(v, w)
        except ValueError:
            raise ValueError(
                f"{self.__class__.__name__} expects `edges`to be an iterable of tuples."
            )

    def _create_adjacency_structure(self, V):
        """Create the underlying adjacency structure for the graph. This is
        a factory method that should be overridden by subclasses.
        """
        if not isinstance(V, int):
            raise ValueError(f"Number of vertices must be an integer! Got {type(V)=}.")

        if V < 0:
            raise ValueError(f"Number of vertices {V=} must be > 0!")

        return [Bag() for _ in range(V)]

    @property
    def V(self):
        """The number of vertices in the graph."""
        return self._V

    @property
    def E(self):
        """The number of edges in the graph."""
        return self._E

    @classmethod
    def fromfile(cls, filename, verbose=False, **kwargs):
        """Construct the graph structure from a file."""
        with Path(filename).open() as fp:
            V = int(fp.readline())
            E = int(fp.readline())
            G = cls(V=V, **kwargs)
            for line in tqdm(fp.readlines(), disable=not verbose):
                v, w = line.strip().split()
                G.add_edge(int(v), int(w))
            assert E == G.E
            return G

    @abstractmethod
    def add_edge(self, v, w):
        """Add an edge from `v` to `w`."""
        pass

    def adj(self, v):
        """Return an iterable of vertices adjacent to `v`."""
        self._validate_vertex(v)
        return self._adj[v]

    # Exercise 4.1.4, 4.2.4
    def has_edge(self, v, w):
        """Return True if an edge from `v` to `w` exists."""
        return w in self.adj(v)

    @property
    def has_parallel_edges(self):
        """Return True if the graph has parallel edges."""
        # Only return True if self._adj[v] has duplicates
        for v in self.vertices():
            seen = set()
            for w in self._adj[v]:
                if w in seen:
                    return True
                seen.add(w)
        return False

    # Exercise 4.1.32
    @property
    def num_parallel_edges(self):
        """The number of parallel edges in the graph."""
        count = 0
        for v in self.vertices():
            seen = set()
            for w in self._adj[v]:
                if w in seen:
                    count += 1
                else:
                    seen.add(w)
        return count

    @property
    def has_self_loop(self):
        """Return True if the graph has a self-loop."""
        for v in self.vertices():
            for w in self._adj[v]:
                if v == w:
                    return True
        return False

    @property
    def num_self_loops(self):
        """The number of self-loops in the graph."""
        return sum(v == w for v in self.vertices() for w in self._adj[v])

    def vertices(self):
        """Return an iterable over the vertices."""
        return range(self._V)

    def _validate_vertex(self, v):
        if not (0 <= v < self.V):
            raise IndexError(f"Vertex index {v=} must be between 0 and {self._V=}!")

    def __str__(self):
        s = f"{self._V} vertices, {self._E} edges\n"
        for v in self.vertices():
            s += f"{v}: " + ' '.join(str(w) for w in self.adj(v)) + '\n'
        return s.strip()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"


# =============================================================================
# =============================================================================
