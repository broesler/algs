#!/usr/bin/env python3
# =============================================================================
#     File: sparse.py
#  Created: 2022-06-10 20:24
#   Author: Bernie Roesler
#
"""
Sparse vector and matrix classes using symbol tables.
"""
# =============================================================================

from algs.search.hash import HashST


class SparseVector:
    """Implements a sparse vector.

    Attributes
    ----------
    N : int
        The size of the vector.
    size : int
        The number of elements in the array.
    """

    def __init__(self, N=1):
        """
        Parameters
        ----------
        N : int
            The size of the vector.
        """
        self.N = N
        self._st = HashST()

    @property
    def size(self):
        """Return the number of elements in the vector."""
        return self._st.size()

    def __setitem__(self, i, v):
        """Put value `v` at integer index `i`."""
        try:
            idxs, vals = iter(i), iter(v)
            for idx, val in zip(idxs, vals):
                self._st[int(idx)] = val
        except TypeError:
            self._st[int(i)] = v

    def __getitem__(self, i):
        """Get the value from index `i`."""
        i = int(i)
        if i in self._st:
            return self._st[i]
        else:
            return 0.0

    def __eq__(self, other):
        if not isinstance(other, SparseVector):
            return NotImplemented
        return False if self.N != other.N else self._st == other._st

    def dot(self, other):
        """Return the dot product of this vector with another."""
        if self.N != other.N:
            raise ValueError('dimension mismatch!')
        s = 0.0
        for i in self._st.keys():
            s += self[i] * other[i]
        return s

    def __matmul__(self, other):
        return self.dot(other)

    def __mul__(self, other):
        """Return the element-wise product of this vector with another."""
        if self.N != other.N:
            raise ValueError('dimension mismatch!')
        # Make a copy
        A = self.__class__(self.N)
        for i, v in self._st.items():
            A[i] = v
        # Multiply element-wise
        for i in A._st.keys():
            A[i] *= other[i]
        return A

    def __add__(self, other):
        """Return the sum of this vector with another."""
        if self.N != other.N:
            raise ValueError('dimension mismatch!')
        # Make a copy
        A = self.__class__(self.N)
        for i, v in self._st.items():
            A[i] = v
        # Add element-wise
        for i in A._st.keys():
            A[i] += other[i]
            if np.isclose(A[i], 0, atol=1e-16):
                del A._st[i]
        return A

    # aliases
    def put(self, i, v):
        self.__setitem__(i, v)

    def get(self, i):
        return self.__getitem__(i)

    def __repr__(self):
        return f"<({self.N},) SparseVector with {self.size()} stored elements."""

    def __str__(self):
        return '\n'.join([f"({i},)\t{v}" for i, v in self])

    # Iterate over coordinates and values
    def __iter__(self):
        yield from self._st.items()


if __name__ == "__main__":
    import numpy as np
    N = 10
    a = SparseVector(N)
    b = SparseVector(N)
    x = np.zeros(10)
    a[[1, 3, 5]] = [1, 3, 5]
    b[[1, 3, 5]] = [1, 3, 5]
    x[[1, 3, 5]] = [1, 9, 25]
    print(a * b)
    print(f"{a @ b = }")
    print(f"{a.dot(b) = }")
    # assert np.allclose(a * b, x)
    assert np.isclose(a @ b, 35.0)
    assert np.isclose(a.dot(b), 35.0)
    print('a + b =')
    print(a + b)
    c = SparseVector(N)
    d = SparseVector(N)
    c[[1, 3, 5]] = [1,  3, 5]
    d[[1, 3, 5]] = [1, -3, 5]
    print('c + d =')
    print(c + d)

# =============================================================================
# =============================================================================
