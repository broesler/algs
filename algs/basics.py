#!/usr/bin/env python3
#==============================================================================
#     File: basics.py
#  Created: 2019-02-08 17:23
#   Author: Bernie Roesler
#
"""
  Description: Basic container algorithms.
"""
#==============================================================================

import operator

from collections import deque
from copy import deepcopy

# TODO implement __lt__ for all classes (in addition to __eq__) for total
# ordering. See:
# <https://docs.python.org/3/library/functools.html#functools.total_ordering>

class Stack():
    """Implements a Stack data structure.

    Parameters
    ----------
    items : iterable
        List of items on the stack, in FIFO order.

    Attributes
    -------
    size : int
        Number of items on the stack.
    is_empty : bool
        True if `size == 0`.
    """
    def __init__(self, items=list()):
        # _items[-1] is "top" of stack
        self._items = list(items[::-1])

    @property
    def size(self):
        return len(self._items)

    @property
    def is_empty(self):
        return (self.size == 0)

    def peek(self):
        """Look at top of stack without popping."""
        return self._items[-1]

    def pop(self):
        """Remove and return item from top of stack."""
        return self._items.pop()

    def push(self, item):
        """Add item to top of stack."""
        self._items.append(item)

    # dunder(-mifflin) methods
    def __iter__(self):
        yield from (self._items[::-1])

    def __bool__(self):
        return bool(self.size)

    def __eq__(self, other):
        return self._items == other._items

    def __repr__(self):
        return '<Stack: ' + self.__str__() + '>'

    def __str__(self):
        return str(list(self._items))


class Queue():
    """Iterable queue object.

    Parameters
    ----------
    items : List of objects
        Items to add to the queue, in FIFO order.

    Attributes
    ----------
    size : int
        Number of items in queue.
    is_empty : bool
        True if `size == 0`
    """
    def __init__(self, items=list()):
        # _items[-1] is "front" of queue
        self._items = deque(items)

    @property
    def size(self):
        return len(self._items)

    @property
    def is_empty(self):
        return (self.size == 0)

    def peek(self):
        """Look at first item in queue without dequeue-ing."""
        return self._items[0]

    def enqueue(self, item):
        """Add item to the end of the queue."""
        self._items.append(item)

    def dequeue(self):
        """Remove and return item from the front of the queue."""
        return self._items.popleft()

    # dunder(-mifflin) methods
    def __iter__(self):
        yield from self._items

    def __eq__(self, other):
        return self._items == other._items

    def __bool__(self):
        return bool(self.size)

    def __repr__(self):
        return '<Queue: ' + self.__str__() + '>'

    def __str__(self):
        return str(list(self._items))


class PriorityQueue():
    """Iterable priority queue object.

    A custom key function can be supplied to determine the sort order.

    Parameters
    ----------
    items : list of objects, optional
        Items to add to the queue.
    kind : str in {'min', 'max'}, optional, default='min'
        How to order the priority queue: minimum item at the front, or maximum.
    key : callable, optional
        Transformation function used in item comparison, *see* `sorted`.

    Attributes
    ----------
    size : int
        Number of items in queue.
    is_empty : bool
        True if `size == 0`

    Notes
    -----
    PQ is implemented as a max/min-heap, using array representation. To
    simplify indices, the root node is index 1. In general, if the parent index
    is `k`, it's children are `2k` and `2k+1`. Likewise, the parent index of
    node `k` is `k//2`.

    Algorithm provides
        * O(1) return the extremum value
        * O(log N) insertion
        * O(log N) remove the extremum value

    See: <https://algs4.cs.princeton.edu/24pq/> for details.
    """
    def __init__(self, items=list(), kind='min', key=None):
        self._items = list([None] + items)  # ignore index 0
        self._op = operator.gt if kind == 'min' else operator.lt
        self._key = key or (lambda x: x)
        # Sink nodes from right-to-left
        for k in range(self.size//2, 0, -1):
            self._sink(k)
        assert self._is_heap()

    @property
    def size(self):
        return len(self._items) - 1  # ignore index 0

    @property
    def is_empty(self):
        return (self.size == 0)

    def peek(self):
        """Look at first item in queue without dequeue-ing."""
        return self._items[1]  # self._items[0] is ALWAYS `None` in heap-land

    def enqueue(self, item):
        """Add item to the queue in proper position."""
        # Add the item at the end of the list, then percolate it up.
        self._items.append(item)
        self._swim(self.size)
        assert self._is_heap()

    def dequeue(self):
        """Remove and return item from the top of the heap."""
        if self.is_empty:
            raise IndexError('Attempting to dequeue from empty PriorityQueue!')
        self._swap(self.size, 1)     # swap root with bottom node
        the_min = self._items.pop()  # remove the root
        self._sink(1)                # sink the new root to reorder
        assert self._is_heap()
        return the_min

    #--------------------------------------------------------------------------
    #        Private helper functions
    #--------------------------------------------------------------------------
    def _sink(self, k):
        """Sink the given node index down to its proper location in the heap."""
        while 2*k <= self.size:
            j = 2*k                                   # move to left child
            if j < self.size and self._comp(j, j+1):
                j += 1                                # move to right child
            if not self._comp(k, j):
                break
            self._swap(k, j)                          # sink the node one level
            k = j

    def _swim(self, k):
        """Swim the given node index up to its proper location in the heap."""
        while k > 1 and self._comp(k//2, k):
            self._swap(k, k//2)
            k = k//2

    def _comp(self, ind_a, ind_b):
        """Compare two items in the heap via their indices.

        .. note::
            If      kind == 'min', True if self._items[a] > self._items[b],
            else if kind == 'max', True if self._items[a] < self._items[b].
        """
        return self._op(self._key(self._items[ind_a]),
                        self._key(self._items[ind_b]))

    def _swap(self, a, b):
        """Swap the location of two items in the heap."""
        self._items[b], self._items[a] = self._items[a], self._items[b]

    def _is_heap(self, k=1):
        """Return True if PriorityQueue is heap-ordered according to `kind`.

        Parameters
        ----------
        k : int in [1, self.size], optional, default = 1
            index of root of sub-heap to check.

        Returns
        -------
        result : bool
            True if self._items is heap-ordered (min/max according to `kind`).
        """
        if k > self.size:
            return True
        # Check the children of k
        left = 2*k
        right = 2*k + 1
        if (left  <= self.size and self._comp(k, left)):  return False
        if (right <= self.size and self._comp(k, right)): return False
        return self._is_heap(left) and self._is_heap(right)

    def __bool__(self):
        return bool(self.size)

    def __eq__(self, other):
        return self._items == other._items

    def __repr__(self):
        return '<PriorityQueue: ' + self.__str__() + '>'

    def __str__(self):
        return str(list(self._items[1:]))

    # Iterator methods: make a copy because in-order iteration is destructive.
    def __iter__(self):
        self._pq_copy = deepcopy(self)
        return self

    def __next__(self):
        if self._pq_copy.is_empty:
            raise StopIteration
        else:
            return self._pq_copy.dequeue()


class IndexPriorityQueue():
    """Iterable priority queue object, with indexing for item access.

    A custom key function can be supplied to customize the sort order.

    Parameters
    ----------
    items : List of objects, optional
        Items to add to the queue.
    kind : str in {'min', 'max'}, optional, default='min'
        How to order the priority queue: minimum item at the front, or maximum.
    key : callable, optional
        Transformation function used in item comparison, *see* `sorted`.

    Attributes
    ----------
    size : int
        Number of items in queue.
    is_empty : bool
        True if `size == 0`

    Notes
    -----
    IndexPQ is implemented as a max/min-heap, using array representation. To
    simplify indices, the root node is index 1. In general, if the parent index
    is `k`, it's children are `2k` and `2k+1`. Likewise, the parent index of
    node `k` is `k//2`.

    Algorithm provides
        * O(1) return the extremum value
        * O(log N) insertion
        * O(log N) remove the extremum value
        * O(log N) change any value in the queue by index
        * O(log N) deletion of any value in the queue by index

    See: <https://algs4.cs.princeton.edu/24pq/> for details.
    """
    # Notes:
    #   pq : a `list` of arbitrary keys, but integer indices
    #   qp : the inverse of pq: `dict` with integer keys, but arbitrary values
    #     ** pq[qp[i]] == qp[pq[i]] == i
    #   items : a dictionary of values, with pq as the keys.
    def __init__(self, data=None, kind='min', key=None):
        self._op = operator.gt if kind == 'min' else operator.lt
        self._key = key or (lambda x: x)  # identity if not given
        self._pq = list([None])
        self._qp = dict()
        self._items = dict()
        # TODO move this class to MutableMapping so init operation is efficient 
        for k, v in data:
            self.enqueue(k, v)

    @property
    def size(self):
        return len(self._pq) - 1  # ignore index 0

    @property
    def is_empty(self):
        return (self.size == 0)

    def peek(self):
        """Look at first item in queue without dequeue-ing."""
        return self._pq[1], self._items[self._pq[1]]

    def enqueue(self, k, item):
        """Add item to the queue with index `k`. 

        .. note:
            Note that the *index* does not correspond to the *priority* in the
            queue! It is for the client to use when accessing specific
            elements.
        """
        # Add the item at the end of the list, then percolate it up.
        self._items[k] = item
        self._pq.append(k)
        self._qp[k] = self.size
        self._swim(self.size)
        assert self._is_heap()

    def dequeue(self):
        """Remove item from the top of the heap. Return its index."""
        if self.is_empty:
            raise Exception('Attempting to dequeue from empty PriorityQueue!')
        self._swap(self.size, 1)       # swap root with bottom node
        idx = self._pq.pop()
        item = self._items.pop(idx)
        self._qp.pop(idx)
        self._sink(1)                  # sink the new root to reorder
        assert self._is_heap()
        return idx, item

    def change(self, k, item):
        """Change item associated with index k to `item`."""
        self._items[k] = item
        self._sink(self._qp[k])
        self._swim(self._qp[k])

    def delete(self, k):
        """Delete arbitrary item associated with index k."""
        idx = self._qp[k]
        self._swap(idx, self.size)  # swap item to end
        to_pop = self._pq.pop()
        self._swim(idx)
        self._sink(idx)
        self._qp.pop(to_pop)
        self._items.pop(to_pop)

    def contains(self, k):
        """Return True if there is an item associated with index k."""
        return k in self._qp  # keys of qp are values in pq

    #--------------------------------------------------------------------------
    #        Private helper functions
    #--------------------------------------------------------------------------
    def _sink(self, k):
        """Sink the given node index down to its proper location in the heap."""
        while 2*k <= self.size:
            j = 2*k
            if j < self.size and self._comp(j, j+1):
                j += 1
            if not self._comp(k, j):
                break
            self._swap(k, j)
            k = j

    def _swim(self, k):
        """Swim the given node index up to its proper location in the heap."""
        while k > 1 and self._comp(k//2, k):
            self._swap(k, k//2)
            k = k//2

    def _comp(self, ind_a, ind_b):
        """Compare two items in the heap.

        .. note::
            If      kind == 'min', True if self._pq[a] < self._pq[b],
            else if kind == 'max', True if self._pq[a] > self._pq[b].
        """
        return self._op(self._key(self._items[self._pq[ind_a]]),
                        self._key(self._items[self._pq[ind_b]]))

    def _swap(self, a, b):
        """Swap the location of two items in the heap."""
        pq, qp = self._pq, self._qp  # aliases for easy reading
        pq[b], pq[a] = pq[a], pq[b]
        qp[pq[b]], qp[pq[a]] = qp[pq[a]], qp[pq[b]]

    def _is_heap(self, k=1):
        """Return True if PriorityQueue is heap-ordered according to `kind`.

        Parameters
        ----------
        k : int in [1, self.size], optional, default = 1
            index of root of sub-heap to check.

        Returns
        -------
        result : bool
            True if self._pq is heap-ordered (min/max according to `kind`).
        """
        if k > self.size:
            return True
        # Check the children of k
        left = 2*k
        right = 2*k + 1
        if (left  <= self.size and self._comp(k, left)):  return False
        if (right <= self.size and self._comp(k, right)): return False
        return self._is_heap(left) and self._is_heap(right)

    def __bool__(self):
        return bool(self.size)

    def __eq__(self, other):
        return self._pq == other._pq

    def __repr__(self):
        return '<PriorityQueue: ' + self.__str__() + '>'

    def __str__(self):
        return str(list(self._pq[1:]))

    # Iterator methods
    def __iter__(self):
        self._pq_copy = deepcopy(self)
        return self

    def __next__(self):
        if self._pq_copy.is_empty:
            raise StopIteration
        else:
            return self._pq_copy.dequeue()


#------------------------------------------------------------------------------
#        Test client
#------------------------------------------------------------------------------
if __name__ == '__main__':
    # TODO move to proper unit testing suite for package
    import string
    from random import shuffle

    def err_test(container, op, err_type=IndexError):
        """Test for raising a given error type.

        Parameters
        ----------
        container : list-like container data type
        op : str
            attribute name of method to test
        err_type : Exception, optional
            error type that object is expected to raise

        Returns
        -------
        None
        """
        while True:
            try:
                getattr(container, op)()  # call the method
            except err_type:
                return
            except Exception as err:
                raise Exception(f'Improper error thrown: {repr(err)}')


    # Test Stack
    s = Stack()
    for i in range(5):
        s.push(i)
    assert s.size == 5
    assert not s.is_empty
    assert 4 == s.peek()
    assert 4 == s.pop()
    # Test iteration -- pop should be in reverse order
    for i, item in zip([3, 2, 1, 0], s):
        assert i == item
    # Test for pop
    err_test(s, 'pop')

    # Test Queue
    q = Queue(['A', 'B', 'C'])
    q.enqueue('D')
    assert q.size == 4
    assert not q.is_empty
    assert 'A' == q.peek()
    assert 'A' == q.dequeue()
    # Elements should be in forwards order
    for c, item in zip(['B', 'C', 'D'], q):
        assert c == item
    # Test dequeue error
    err_test(q, 'dequeue')

    # Shuffled alphabet data with indices
    data_s = string.ascii_uppercase
    idx_s = list(range(len(data_s)))
    idx = idx_s.copy()
    shuffle(idx)
    data = [data_s[i] for i in idx]

    # Test maxPQ
    pq = PriorityQueue(data, kind='max')
    assert not pq.is_empty
    assert pq.size == 26
    assert 'Z' == pq.peek()
    assert 'Z' == pq.dequeue()
    assert 'Y' == pq.dequeue()
    assert 'X' == pq.dequeue()
    assert 'W' == pq.peek()
    for c in ['X', 'Y', 'Z']:
        pq.enqueue(c)
    # implicitly test iteration
    assert ''.join(pq) ==  string.ascii_uppercase[::-1]
    # Test dequeue error
    err_test(pq, 'dequeue')

    # Test MinPQ
    pq = PriorityQueue(data, kind='min')
    assert 'A' == pq.dequeue()
    assert 'B' == pq.dequeue()
    assert 'C' == pq.dequeue()
    assert 'D' == pq.peek()
    for c in ['A', 'B', 'C']:
        pq.enqueue(c)
    # implicitly test iteration
    assert ''.join(pq) ==  string.ascii_uppercase

    # Test IndexMinPQ
    pq = IndexPriorityQueue(zip(idx, data), kind='min')
    assert pq.size == 26
    assert (0, 'A') == pq.dequeue()
    assert (1, 'B') == pq.dequeue()
    assert (2, 'C') == pq.dequeue()
    assert pq.size == 23
    assert (3, 'D') == pq.peek()
    for i, c in [(0, 'A'), (1, 'B'), (2, 'C')]:
        pq.enqueue(i, c)
    assert list([item[0] for item in pq]) == idx_s
    assert ''.join([item[1] for item in pq]) == string.ascii_uppercase

    # Test `change` item
    pq.change(0, 'ZZZ')
    assert pq.contains(0)
    assert list([item[0] for item in pq]) == idx_s[1:] + [0]
    assert ''.join([item[1] for item in pq]) == string.ascii_uppercase[1:] + 'ZZZ'
    pq.change(0, 'A')
    assert pq.contains(0)
    assert list([item[0] for item in pq]) == idx_s
    assert ''.join([item[1] for item in pq]) == string.ascii_uppercase

    # Test 'delete' item
    pq.delete(0)
    assert not pq.contains(0)
    assert list([item[0] for item in pq]) == idx_s[1:]
    assert ''.join([item[1] for item in pq]) == string.ascii_uppercase[1:]

    # Internal checks
    for i in range(1, len(pq._pq)-1):
        assert pq._pq[pq._qp[i]] == i

    print('All tests passed.')

#==============================================================================
#==============================================================================
