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

import numpy as np
from operator import iadd, isub, imul, itruediv

from algs.search.hash import HashST
from algs.search.set import MathSet


# TODO `.todense()` method that returns an `np.ndarray`.
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

    @property
    def shape(self):
        """Return the number of elements in the vector."""
        return (self.N,)

    def __setitem__(self, i, v):
        """Put value `v` at integer index `i`."""
        try:
            idxs, vals = iter(i), iter(v)
            for idx, val in zip(idxs, vals):
                assert idx < self.N
                self._st[int(idx)] = val
        except TypeError:
            assert 0 <= i < self.N
            self._st[int(i)] = v

    def __getitem__(self, i):
        """Get the value from index `i`."""
        i = int(i)
        assert 0 <= i < self.N
        if i in self._st:
            return self._st[i]
        else:
            return 0

    def copy(self):
        """Make a copy."""
        A = self.__class__(self.N)
        for i, v in self._st.items():
            A[i] = v
        return A

    # TODO return (N,) bool array for each element.
    def __eq__(self, other):
        if not isinstance(other, SparseVector):
            return NotImplemented
        return False if self.N != other.N else self._st == other._st

    def dot(self, other):
        """Return the dot product of this vector with another."""
        if self.N != other.N:
            raise ValueError('dimension mismatch!')
        s = 0
        for i in self._st.keys():
            s += self[i] * other[i]
        return s

    def __matmul__(self, other):
        return self.dot(other)

    # Exercise 3.5.16
    def __add__(self, other):
        """Return the sum of this vector with another."""
        return self._op(other, op=iadd)

    def __sub__(self, other):
        """Return the difference of this vector with another."""
        return self._op(other, op=isub)

    def __mul__(self, other):
        """Return the element-wise product of this vector with another."""
        return self._op(other, op=imul)

    def __truediv__(self, other):
        """Return the element-wise division of this vector by another."""
        return self._op(other, op=itruediv)

    __radd__ = __add__  # allow 1 + a or a + 1
    __rsub__ = __sub__
    __rmul__ = __mul__

    def _op(self, other, op):
        if isinstance(other, self.__class__):
            return self.__op(other, op=op)
        else:
            return self._scale(other, op=op)

    def __op(self, other, op):
        """Return the element-wise product of this vector with another."""
        if self.N != other.N:
            raise ValueError('dimension mismatch!')
        A = self.copy()
        if op in [iadd, isub]:
            iters = set(A._st.keys()).union(set(other._st.keys()))
        else:
            iters = A._st.keys()
        for i in iters:
            A[i] = op(A[i], other[i])
            if np.isclose(A[i], 0, atol=1e-16):
                del A._st[i]
        return A

    def _scale(self, scalar, op):
        """Return an operation on this vector with a scalar."""
        A = self.copy()
        for i in A._st.keys():
            A[i] = op(A[i], scalar)
        return A

    # aliases
    def put(self, i, v):
        self.__setitem__(i, v)

    def get(self, i):
        return self.__getitem__(i)

    def __str__(self):
        return '\n'.join([f"({i},)\t{v}" for i, v in self])

    def __repr__(self):
        return f"<({self.N},) {self.__class__.__name__} with {self.size} stored elements."""

    # Iterate over coordinates and values
    def __iter__(self):
        yield from self._st.items()

    def todense(self):
        A = np.zeros((self.N,))
        for k, v in self:
            A[k] = v
        return A


# Exercise 3.5.23
# TODO constructors for row/column vectors
class SparseMatrix():
    """Implements a sparse matrix of size `M x N`."""

    def __init__(self, shape):
        self.M = shape[0]
        self.N = shape[1]
        self._size = 0
        self._st = HashST()  # _st represents rows

    @property
    def size(self):
        return self._size

    @property
    def shape(self):
        """Return the number of elements in the vector."""
        return (self.M, self.N)

    def copy(self):
        """Make a copy."""
        A = self.__class__((self.M, self.N))
        for (i, j), v in self:
            A[i, j] = v
        return A

    def __setitem__(self, k, v):
        # Parse indices
        if isinstance(k, int):
            i, j = k, None
        else:
            i, j = k
        # if not (0 <= i < self.M):
        #     raise IndexError(f"Cannot index row {i} in matrix of size ({self.M}, {self.N})!")
        if i not in self._st:
            self._st[i] = SparseVector(self.N)
        if j is not None:
            self._st[i][j] = v
            self._size += 1
        else:
            self._st[i] = v
            self._size += v.size

    def __getitem__(self, k):
        # Parse indices
        if isinstance(k, int):
            i, j = k, None
        else:
            i, j = k
        # Return value
        if i in self._st:
            if j is not None:
                return self._st[i][j]
            else:
                return self._st[i]
        else:
            return 0

    def col(self, j):
        """Return the `j`th column."""
        c = SparseVector(self.M)
        for i in self._st.keys():
            c[i] = self[i, j]
        return c

    def transpose(self):
        A = self.__class__((self.M, self.N))
        for (i, j), v in self:
            A[j, i] = v
        return A

    @property
    def T(self):
        return self.transpose()

    def __add__(self, other):
        if not isinstance(other, SparseMatrix):
            return NotImplemented
        if self.shape != other.shape:
            raise ValueError(f"Cannot add {self.shape} to {other.shape}")
        A = self.copy()
        iters = set(self._st.keys()).union(set(other._st.keys()))
        for i in iters:
            A._st[i] = self._st[i] + other._st[i]
        return A

    def dot(self, x):
        """Return the matrix multiplication of this matrix with another."""
        if not (isinstance(x, SparseVector) 
                or isinstance(x, SparseMatrix)):
            return NotImplemented
        if self.shape[1] != x.shape[0]:
            raise ValueError(f"Cannot multiply {self.shape} to {x.shape}")
        if len(x.shape) > 1:
            b = SparseMatrix((self.N, x.M))
        else:
            b = SparseVector(self.N)
        for i in self._st.keys():
            b[i] = self[i].dot(x)
        return b

    def __matmul__(self, x):
        return self.dot(x)

    def __str__(self):
        return '\n'.join([f"({i}, {j})\t{v}" for (i, j), v in self])

    def __repr__(self):
        return f"<{self.shape} {self.__class__.__name__} with {self.size} stored elements."""

    def _items(self):
        items = list()
        for i, row in self._st.items():
            for j, v in row:
                items.append(((i, j), v))
        return items

    def __iter__(self):
        yield from self._items()
        
    def todense(self):
        A = np.zeros((self.M, self.N))
        for (i, j), v in self:
            A[i, j] = v
        return A


if __name__ == "__main__":
    N = 10
    a = SparseVector(N)
    b = SparseVector(N)
    x = np.zeros(10)
    a[[1, 3, 6, 7]] = [2, 4, 6, 7]
    b[[1, 3, 6, 8]] = [1, 3, 5, 7]
    x[[1, 3, 6]] = [2, 12, 30]
    print('a =', a.todense())
    print('b =', b.todense())
    print('a = ')
    print(a)
    assert np.allclose((3*a).todense(), np.r_[0, 6, 0, 12, 0, 0, 18, 21, 0, 0])
    assert np.allclose((3 + a).todense(), np.r_[0, 5, 0, 7, 0, 0, 9, 10, 0, 0])
    print(f"{a @ b = }")
    print(f"{a.dot(b) = }")
    assert np.allclose((a * b).todense(), x)
    assert np.isclose(a @ b, 44.0)
    assert np.isclose(a.dot(b), 44.0)
    assert np.allclose((a + b).todense(), np.r_[0, 3, 0, 7, 0, 0, 11, 7, 7, 0])
    assert np.allclose((a - b).todense(), np.r_[0, 1, 0, 1, 0, 0, 1, 7, -7, 0])
    # print('a / b =')
    # print(a / b)
    # Test close to 0
    c = SparseVector(N)
    d = SparseVector(N)
    c[[1, 3, 5]] = [1,  3, 5]
    d[[1, 3, 5]] = [1, -3, 5]
    assert np.allclose((c + d).todense(), np.r_[0, 2, 0, 0, 0, 10, 0, 0, 0, 0])
    assert np.allclose((c - d).todense(), np.r_[0, 0, 0, 6, 0, 0, 0, 0, 0, 0])

    # Test matrices
    N = 4
    I = SparseMatrix((N, N))  # identity
    A = SparseMatrix((N, N))  # first forward difference
    for i in range(N):
        I[i, i] =  1
        if i > 0:
            A[i, i-1] = -1
        A[i, i] = 1
    print('----- Matrices -----')
    print(I.todense())
    print(I)
    print('A')
    print(A.todense())
    print('A.T')
    print(A.T.todense())
    print('A + A.T')
    print((A + A.T).todense())
    x = SparseVector(N)
    x[[0, 1, 2, 3]] = [1, 1, 1, 1]
    print('A @ x')
    print(A @ x)  # delta[0] vector
    print((A[0] @ A).todense())  # select first row
    print((A @ A[0]).todense())  # select first column
    print('A @ I')
    print((A @ I).todense())
    print('I @ A')
    print((I @ A).todense())
    print('A.T @ A')
    print((A.T @ A).todense())
    print('A @ A.T')
    print((A @ A.T).todense())

# =============================================================================
# =============================================================================
