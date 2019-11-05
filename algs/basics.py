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

import operator as _operator

from collections import deque as _deque
from collections.abc import MutableMapping as _MutableMapping
from copy import deepcopy as _deepcopy

__all__ = ['Stack', 'Queue', 'PriorityQueue', 'IndexPQ']


def _equals(self, other):
    if isinstance(other, self.__class__):
        return self._items == other._items
    else:
        raise TypeError("'==' not supported between instances of "\
                        f"'{self.__class__.__name__}' and '{other.__class__.__name__}'")


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

    def __len__(self):
        return self.size

    def __eq__(self, other):
        return _equals(self, other)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.__str__())

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
        self._items = _deque(items)

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
        return _equals(self, other)

    def __len__(self):
        return self.size


    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.__str__())

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
        self._items = list([None] + list(items))  # ignore index 0
        self._op = _operator.gt if kind == 'min' else _operator.lt
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

    def __len__(self):
        return self.size

    def __eq__(self, other):
        return _equals(self, other)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.__str__())

    def __str__(self):
        return str(list(self._items[1:]))

    # Iterator methods: make a copy because in-order iteration is destructive.
    def __iter__(self):
        self._pq_copy = _deepcopy(self)
        return self

    def __next__(self):
        if self._pq_copy.is_empty:
            raise StopIteration
        else:
            return self._pq_copy.dequeue()


class IndexPQ(_MutableMapping):
    """Priority queue as a native python dictionary. 'Pythonic' version of
    IndexPriorityQueue.

    A custom key function can be supplied to customize the sort order.

    Parameters
    ----------
    items : map or iterable of objects, optional
        List or Dictionary of (key, value) pairs to add to the queue.
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
    #   pq : a `list` of keys corresponding to `items` (with integer indices)
    #   qp : the inverse of pq: `dict` with integer keys, but arbitrary values
    #     ** pq[qp[i]] == qp[pq[i]] == i
    #   items : a dictionary of given values, with pq values as the keys.
    # TODO
    #   * move this to its own package/file, implement additional tests for
    #     initialization, timing tests to show log N behavior.
    #   * create pq of objects with attributes and test the key function
    #   * implement self.copy()
    #   * write setter functions for self.kind and self.key to reorganize the
    #     heap if they are changed.
    def __init__(self, items=None, kind='min', key=None):
        self.kind = kind
        self._op = _operator.gt if self.kind == 'min' else _operator.lt
        self.key = key or (lambda x: x)  # identity if not given
        self._pq = list([None])
        self._qp = dict()
        self._items = dict()
        if items is not None:
            self.update(items)  # __setitem__ takes care of enqueuing

    #-------------------------------------------------------------------------- 
    #        Public API
    #--------------------------------------------------------------------------
    @property
    def size(self):
        return len(self._pq) - 1  # ignore index 0

    @property
    def is_empty(self):
        return self.size == 0

    def peek(self):
        """Look at first item in queue without dequeue-ing.

        Returns
        -------
        key, value : tuple
            The key associated with the extremum item, and the item itself.
        """
        if len(self._pq) > 1:
            idx = self._pq[1]
            return idx, self._items[idx]
        else:
            return None, None

    def enqueue(self, k, item):
        """Add an `item` to the queue with index `k`. 

        .. note:
            Note that the *index* does not correspond to the *priority* in the
            queue! The index is for the client to use when accessing specific
            elements.
        """
        # Add the item at the end of the list, then percolate it up.
        self._items[k] = item
        self._pq.append(k)
        self._qp[k] = self.size
        self._swim(self.size)
        assert self._is_heap()

    def dequeue(self):
        """Remove item from the top of the heap.

        Returns
        -------
        key, value : tuple
            The key associated with the extremum item, and the item itself.
        """
        if self.is_empty:
            raise Exception('Attempting to dequeue from empty PriorityQueue!')
        self._swap(self.size, 1)       # swap root with bottom node
        idx = self._pq.pop()
        item = self._items.pop(idx)
        if idx in self._qp: 
            del self._qp[idx]
        self._sink(1)                  # sink the new root to reorder
        assert self._is_heap()
        return idx, item

    # Typical dictionary methods not inherited by MutableMapping
    def copy(self):
        """Return a shallow copy of the IndexPQ.

        .. note:
            Because the shallow copy iterates over the current object, the keys
            in the copy will be in *sorted* order, so self.copy()._pq will
            *not* match self._pq."""
        return self.__class__(self, kind=self.kind, key=self.key)

    @classmethod
    def fromkeys(cls, iterable, value=None, **kwargs):
        """Create a new IndexPQ object from given iterable."""
        return cls(((k, value) for k in iterable), **kwargs)

    #--------------------------------------------------------------------------
    #        Private helper functions
    #--------------------------------------------------------------------------
    def _change_item(self, k, item):
        """Change item associated with index `k` to `item`."""
        self._items[k] = item
        self._sink(self._qp[k])
        self._swim(self._qp[k])

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
        try:
            return self._op(self.key(self._items[self._pq[ind_a]]),
                            self.key(self._items[self._pq[ind_b]]))
        except TypeError:  # `<` and `>` don't like `None` values
            return False

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

    #-------------------------------------------------------------------------- 
    #        Python object methods
    #--------------------------------------------------------------------------
    def __len__(self):
        return self.size

    def __eq__(self, other):
        return _equals(self, other)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.__str__())

    def __str__(self):
        # show list of (key, value) pairs in heap-order
        return str(dict([(x, self._items[x]) for x in self._pq[1:]]))

    def __contains__(self, k):
        """Return True if index `k` is in the queue."""
        return k in self._qp  # keys of qp are values in pq

    def __iter__(self):
        """Return an iterator with a copy."""
        self._pq_copy = _deepcopy(self)
        return self

    def __next__(self):
        """Iterate over keys from a copy, in specified priority order."""
        if self._pq_copy.is_empty:
            raise StopIteration
        else:
            return self._pq_copy.dequeue()[0]  # iterate over keys

    #-------------------------------------------------------------------------- 
    #        _MutableMapping required methods
    #--------------------------------------------------------------------------
    def __len__(self):
        return self.size

    def __getitem__(self, k):
        return self._items[k]

    def __setitem__(self, k, item):
        if k in self:
            self._change_item(k, item)
        else:
            self.enqueue(k, item)

    def __delitem__(self, k):
        """Delete the item associated with index `k`."""
        idx = self._qp[k]
        self._swap(idx, self.size)  # swap item to end
        to_del = self._pq.pop()
        self._swim(idx)             # reorganize the heap
        self._sink(idx)
        if to_del in self._qp:    
            del self._qp[to_del]    # remove the item
        if to_del in self._items:
            del self._items[to_del]


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
    should_be(s.size, 5)
    should_be(s.is_empty, False)
    should_be(4, s.peek())
    should_be(4, s.pop())
    # Test iteration -- pop should be in reverse order
    for i, item in zip([3, 2, 1, 0], s):
        should_be(i, item)
    # Test for pop
    err_test(s, 'pop')

    # Test Queue
    q = Queue(['A', 'B', 'C'])
    q.enqueue('D')
    should_be(q.size, 4)
    should_be(q.is_empty, False)
    should_be('A', q.peek())
    should_be('A', q.dequeue())
    # Elements should be in forwards order
    for c, item in zip(['B', 'C', 'D'], q):
        should_be(c, item)
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
    should_be(pq.is_empty, False)
    should_be(pq.size, 26)
    should_be('Z', pq.peek())
    should_be('Z', pq.dequeue())
    should_be('Y', pq.dequeue())
    should_be('X', pq.dequeue())
    should_be('W', pq.peek())
    for c in ['X', 'Y', 'Z']:
        pq.enqueue(c)
    # implicitly test iteration
    should_be(''.join(pq), string.ascii_uppercase[::-1])
    # Test dequeue error
    err_test(pq, 'dequeue')

    # Test MinPQ
    pq = PriorityQueue(data, kind='min')
    should_be('A', pq.dequeue())
    should_be('B', pq.dequeue())
    should_be('C', pq.dequeue())
    should_be('D', pq.peek())
    for c in ['A', 'B', 'C']:
        pq.enqueue(c)
    # implicitly test iteration
    should_be(''.join(pq), string.ascii_uppercase)

    # Test IndexMinPQ
    pq = IndexPQ(zip(idx, data), kind='min')
    should_be(len(pq), 26)
    should_be((0, 'A'), pq.dequeue())
    should_be((1, 'B'), pq.dequeue())
    should_be((2, 'C'), pq.dequeue())
    should_be(len(pq), 23)
    should_be((3, 'D'), pq.peek())
    for i, c in [(0, 'A'), (1, 'B'), (2, 'C')]:
        pq.enqueue(i, c)
    should_be(list(pq.keys()), idx_s)
    should_be(''.join(pq.values()), string.ascii_uppercase)

    # Test `change` item
    pq[0] = 'ZZZ'
    should_be(0 in pq, True)
    should_be(list(pq.keys()), idx_s[1:] + [0])
    should_be(''.join(pq.values()), string.ascii_uppercase[1:] + 'ZZZ')
    pq[0] = 'A'
    should_be(0 in pq, True)
    should_be(list(pq.keys()), idx_s)
    should_be(''.join(pq.values()), string.ascii_uppercase)

    # Test 'delete' item
    i = 0  # removes (0, 'A')
    item = pq[i]  # store value for later
    del pq[i]
    should_be(i not in pq, True)
    should_be(list(pq.keys()), idx_s[:i] + idx_s[i+1:])
    should_be(''.join(pq.values()),   string.ascii_uppercase[:i]\
                                    + string.ascii_uppercase[i+1:])

    # Re-add item for completeness
    pq[i] = item

    # Internal checks
    for i in range(len(pq._pq)-1):
        should_be(pq._pq[pq._qp[i]], i)

    # Equality checks
    pq1 = IndexPQ(zip(idx, data), kind='min')
    pq2 = IndexPQ(zip(idx, data), kind='min')
    should_be(pq1, pq2)
    del pq1, pq2

    # Copy check
    pq_copy = pq.copy()
    should_be(pq_copy, pq)

    pq_fromkeys = pq.fromkeys(idx)

    # Summary
    if fails > 0:
        print(f"{fails}/{tests} tests failed")
    else:
        print(f"All {tests} tests passed!")


#==============================================================================
#==============================================================================
