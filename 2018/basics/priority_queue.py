#!/usr/bin/env python3
#==============================================================================
#     File: priority_queue.py
#  Created: 2019-03-02 12:08
#   Author: Bernie Roesler
#
"""
Description: Priority Queue implementation

PQ is implemented as a max/min-heap, using array representation. To simplify
indices, the root node is index 1. In general, if the parent index is k, it's
children are 2k and 2k+1. Likewise, the parent index of node k is k/2.

See: <https://algs4.cs.princeton.edu/24pq/> for details.
"""
#==============================================================================

import copy
import operator

class PriorityQueue():
    """Iterable priority queue object.

    Parameters
    ----------
    items : List of objects, optional
        Items to add to the queue.
    kind : str in {'min', 'max'}, optional, default='min'
        How to order the priority queue: minimum item at the front, or maximum.

    Attributes
    ----------
    size : int
        Number of items in queue.
    is_empty : bool
        True if `size == 0`
    """
    def __init__(self, items=list(), kind='min'):
        self._op = operator.lt if kind == 'min' else operator.gt
        self._items = list([None])  # ignore index 0
        self._items.extend(items)
        # Sink nodes from right-to-left
        for k in range(self.size // 2, 0, -1):
            self._sink(k)
        assert self._is_heap()

    @property
    def size(self):
        return len(self._items) - 1

    @property
    def is_empty(self):
        return (self.size == 0)

    def peek(self):
        """Look at first item in queue without dequeue-ing."""
        # self._items[0] is ALWAYS `None` in heap-land
        return self._items[1]

    def enqueue(self, item):
        """Add item to the queue in proper position."""
        # Add the item at the end of the list, then percolate it up.
        self._items.append(item)
        self._swim(self.size)
        assert self._is_heap()

    def dequeue(self):
        """Remove and return item from the top of the heap."""
        self._swap(self.size, 1)              # swap root with bottom node
        the_min = self._items.pop(self.size)  # remove the root
        self._sink(1)                         # sink the new root to reorder
        assert self._is_heap()
        return the_min

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

    def _comp(self, a, b):
        """Compare two items in the heap. 
        
        If      kind == 'min', returns True if self._items[a] < self._items[b],
        else if kind == 'max', returns True if self._items[a] > self._items[b].
        """
        return self._op(self._items[a], self._items[b])

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
        if (left  <= self.size and self._comp(k, left)):
            return False
        if (right <= self.size and self._comp(k, right)):
            return False
        return self._is_heap(left) and self._is_heap(right)

    #-------------------------------------------------------------------------- 
    #        Python dunder (mifflin) methods
    #--------------------------------------------------------------------------
    def __bool__(self):
        return bool(self.size)

    def __repr__(self):
        return '<PriorityQueue: ' + self.__str__() + '>'

    def __str__(self):
        return str(self._items[1:]) 

    # Iterator methods
    def __iter__(self):
        self._pq = copy.deepcopy(self)
        return self

    def __next__(self):
        if self._pq.is_empty:
            raise StopIteration
        else:
            return self._pq.dequeue() 


#------------------------------------------------------------------------------ 
#        Test client
#------------------------------------------------------------------------------
if __name__ == '__main__':
    import string
    from basics.stack import Stack
    pq = PriorityQueue(list(string.ascii_uppercase), kind='min')
    assert not pq.is_empty
    assert pq.size == 26
    assert 'Z' == pq.peek()
    assert 'Z' == pq.dequeue()
    assert 'Y' == pq.dequeue()
    assert 'X' == pq.dequeue()
    for a in ['X', 'Y', 'Z']:
        pq.enqueue(a)
    s = Stack()
    for a in pq:
        s.push(a)
    assert ''.join(s) == string.ascii_uppercase


#==============================================================================
#==============================================================================
