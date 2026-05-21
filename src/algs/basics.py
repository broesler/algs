#!/usr/bin/env python3
# =============================================================================
#     File: basics.py
#  Created: 2019-02-08 17:23
#   Author: Bernie Roesler
#
"""
  Description: Basic container algorithms.
"""
# =============================================================================

import operator as _operator
import random

from abc import ABC
from collections import deque
from collections.abc import MutableMapping
from copy import deepcopy

__all__ = ['Collection', 'Bag', 'Stack', 'Queue', 'PriorityQueue', 'IndexPQ',
           'RandomBag', 'RandomQueue', 'DoubleList']


class Collection(ABC):
    # An abstract base class implementing a collection class. The concrete data
    # types differ in the specification of which object is to be removed or
    # examined next.
    """
    Attributes
    -------
    size : int
        Number of items on the stack.
    is_empty : bool
        True if `size == 0`.
    """

    def __init__(self, items=None):
        """
        Parameters
        ----------
        items : iterable
            List of items to store in the collection.
        """
        items = items or []
        self._items = list(items)

    @property
    def size(self):
        return len(self._items)

    @property
    def is_empty(self):
        return self.size == 0

    def _empty_check(self):
        """General assertion that container is not empty before indexing."""
        if self.is_empty:
            raise IndexError(f"{self.__class__.__name__} is empty!")

    def __len__(self):
        return self.size

    def __eq__(self, other):
        # Assume order matters, so check that the items lists are identical.
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._items == other._items

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __str__(self):
        def a_list(a):
            return ', '.join(repr(k) for k in a)

        a = list(self)  # use iteration to print the object
        if len(self) < 30:
            return str(a)
        else:
            # shorten for printing
            return '[' + a_list(a[:3]) + ' ... ' + a_list(a[-3:]) + ']'

    # NOTE __contains__ automatically defaults to using __iter__
    def __iter__(self):
        yield from self._items


class Bag(Collection):
    __doc__ = f"""Implements a Bag data structure.
              {Collection.__doc__}"""

    def add(self, item):
        """Add item to the bag."""
        self._items.append(item)

    # TODO how to test equality when items cannot be sorted?
    # i.e. a string and an int in the same Bag.
    # def __eq__(self, other):
    #     # When comparing Bags, order does not matter, so sort the items first.
    #     if not isinstance(other, Bag):
    #         raise NotImplemented
    #     return sorted(self._items) == sorted(other._items)


# Exercise 1.3.4
class RandomBag(Bag):
    __doc__ = f"""Implements a Bag data structure, but items are iterated in
              a random order.
              {Collection.__doc__}"""

    def __iter__(self):
        random.shuffle(self._items)
        yield from self._items


class Stack(Collection):
    __doc__ = f"""Implements a Stack data structure.
              {Collection.__doc__}"""

    def __init__(self, items=None):
        super().__init__(items)
        # _items[-1] is "top" of stack
        self._items = list(reversed(self._items))

    def peek(self):
        """Look at top of stack without popping."""
        self._empty_check()
        return self._items[-1]

    def pop(self):
        """Remove and return item from top of stack."""
        self._empty_check()
        return self._items.pop()

    def push(self, item):
        """Add item to top of stack."""
        self._items.append(item)

    # dunder(-mifflin) methods
    def __iter__(self):
        yield from reversed(self._items)

    def __str__(self):
        return str(list(reversed(self._items)))


class Queue(Collection):
    __doc__ = f"""Iterable queue object.
              {Collection.__doc__}"""

    def __init__(self, items=None):
        super().__init__(items)
        # _items[-1] is "front" of queue
        self._items = deque(self._items)

    def peek(self):
        """Look at first item in queue without dequeue-ing."""
        self._empty_check()
        return self._items[0]

    def enqueue(self, item):
        """Add item to the end of the queue."""
        self._items.append(item)

    def dequeue(self):
        """Remove and return item from the front of the queue."""
        self._empty_check()
        return self._items.popleft()


# Exercise 1.3.32
class Steque(Collection):
    __doc__ = f"""Implements a stack-ended queue data structure.
              {Collection.__doc__}"""

    def __init__(self, items=None):
        super().__init__(items)
        # _items[-1] is the "back of the line", onto which items are added.
        self._items = deque(self._items)

    def peek(self):
        """Look at first item in queue without popping."""
        self._empty_check()
        return self._items[0]

    def enqueue(self, item):
        """Add item to the end of the stequeue."""
        self._items.append(item)

    def pop(self):
        """Remove and return item from the front of the steque."""
        self._empty_check()
        return self._items.popleft()

    def push(self, item):
        """Push item onto the front of the steque."""
        self._items.appendleft(item)


# Exercise 1.3.35
class RandomQueue(Queue):
    __doc__ = f"""Iterable queue object, but in random order.
              {Collection.__doc__}"""

    def dequeue(self):
        """Remove and return a random item."""
        self._empty_check()
        k = random.randrange(0, self.size)
        v = self._items[k]
        del self._items[k]
        return v

    def sample(self):
        """Return a random item without deletion."""
        self._empty_check()
        k = random.randrange(0, self.size)
        return self._items[k]

    def __iter__(self):
        """Return an iterator over the items in a random order."""
        random.shuffle(self._items)
        yield from self._items


class PriorityQueue(Collection):
    __doc__ = f"""Iterable priority queue object.

    A custom key function can be supplied to determine the sort order.
    {Collection.__doc__}

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

    def __init__(self, items=None, kind='min', key=None):
        super().__init__(items)
        self._items = list([None] + self._items)  # ignore index 0
        self._op = _operator.gt if kind == 'min' else _operator.lt
        self._key = key or (lambda x: x)
        # Sink nodes from right-to-left
        for k in range(self.size//2, 0, -1):
            self._sink(k)
        assert self._is_heap()

    __init__.__doc__ = f"""{Collection.__init__.__doc__}
    kind : str in {'min', 'max'}, optional, default='min'
        How to order the priority queue: minimum item at the front, or maximum.
    key : callable, optional
        Transformation function used in item comparison, *see* `sorted`.
    """

    @property
    def size(self):
        return len(self._items) - 1  # ignore index 0

    def peek(self):
        """Look at first item in queue without dequeue-ing."""
        self._empty_check()
        return self._items[1]  # self._items[0] is ALWAYS `None` in heap-land

    def enqueue(self, item):
        """Add item to the queue in proper position."""
        # Add the item at the end of the list, then percolate it up.
        self._items.append(item)
        self._swim(self.size)
        assert self._is_heap()

    def dequeue(self):
        """Remove and return item from the top of the heap."""
        self._empty_check()
        self._swap(self.size, 1)     # swap root with bottom node
        the_min = self._items.pop()  # remove the root
        self._sink(1)                # sink the new root to reorder
        assert self._is_heap()
        return the_min

    # -------------------------------------------------------------------------
    #        Private helper functions
    # -------------------------------------------------------------------------
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


class IndexPQ(Collection, MutableMapping):
    __doc__ = f"""Priority queue as a native python dictionary. 'Pythonic' version of
    IndexPriorityQueue.

    A custom key function can be supplied to customize the sort order.
    {Collection.__doc__}
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
    #   * replace `dict` with `list` and proper resizing code.
    #   * move this to its own package/file, implement additional tests for
    #     initialization, timing tests to show log N behavior.
    #   * create pq of objects with attributes and test the key function
    #   * implement self.copy()
    #   * write setter functions for self.kind and self.key to reorganize the
    #     heap if they are changed.

    def __init__(self, items=None, kind='min', key=None):
        """
        Parameters
        ----------
        items : map or iterable of objects, optional
            List or Dictionary of (key, value) pairs to add to the queue.
        kind : str in {'min', 'max'}, optional, default='min'
            How to order the priority queue: minimum item at the front, or maximum.
        key : callable, optional
            Transformation function used in item comparison, *see* `sorted`.
        """
        self.kind = kind
        self._op = _operator.gt if self.kind == 'min' else _operator.lt
        self.key = key or (lambda x: x)  # identity if not given
        self._pq = list([None])
        self._qp = dict()
        self._items = dict()
        if items is not None:
            self.update(items)  # __setitem__ takes care of enqueuing

    # -------------------------------------------------------------------------
    #        Public API
    # -------------------------------------------------------------------------
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
        self._empty_check()
        idx = self._pq[1]
        return idx, self._items[idx]

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
        self._empty_check()
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

    # -------------------------------------------------------------------------
    #        Private helper functions
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    #        Python object methods
    # -------------------------------------------------------------------------
    def __str__(self):
        # show list of (key, value) pairs in heap-order
        return str(dict([(x, self._items[x]) for x in self._pq[1:]]))

    def __contains__(self, k):
        """Return True if index `k` is in the queue."""
        return k in self._qp  # keys of qp are values in pq

    def __iter__(self):
        """Return an iterator with a copy."""
        self._pq_copy = deepcopy(self)
        return self

    def __next__(self):
        """Iterate over keys from a copy, in specified priority order."""
        if self._pq_copy.is_empty:
            raise StopIteration
        else:
            return self._pq_copy.dequeue()[0]  # iterate over keys

    # -------------------------------------------------------------------------
    #        MutableMapping required methods
    # -------------------------------------------------------------------------
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


# Exercise 1.3.31
class DoubleList(Collection):
    """Implements a doubly-linked list."""

    class _DoubleNode():
        """A node in a doubly-linked list."""
        def __init__(self, data, prev=None, next=None):
            self.data = data
            self.next = next
            self.prev = prev

        def __str__(self):
            prev_str = str(repr(self.prev.data)) if self.prev else 'None'
            next_str = str(repr(self.next.data)) if self.next else 'None'
            return f"({repr(self.data)}:, P:{prev_str}, N:{next_str})"

        def __repr__(self):
            return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __init__(self, items=None):
        self._first = None  # pointers to ends of list
        self._last = None
        self._N = None
        items = items or []
        for item in items:
            self.add_back(item)

    @property
    def _items(self):
        """Return a list of the items in order."""
        out = list()
        x = self._first
        while x:
            out.append(x.data)
            x = x.next
        return out

    def add_front(self, item):
        """Add an item to the front of the list."""
        x = self._DoubleNode(item, next=self._first)
        if self._first is None:
            self._first = x
            self._last = x
        else:
            self._first.prev = x
        self._first = x

    def add_back(self, item):
        """Add an item to the back of the list."""
        x = self._DoubleNode(item, prev=self._last)
        if self._last is None:
            self._first = x
            self._last = x
        else:
            self._last.next = x
        self._last = x

    def remove_front(self):
        """Remove and return the first node in the list."""
        self._empty_check()
        x = self._first
        self._first = self._first.next
        self._first.prev = None
        return x

    def remove_back(self):
        """Remove the last node in the list."""
        self._empty_check()
        x = self._last
        self._last = self._last.prev
        self._last.next = None
        return x

    def remove(self, x):
        """Remove a given Node from the list."""
        if self._first is x:
            self._first = x.next
            self._first.prev = None
        elif self._last is x:
            self._last = x.prev
            self._last.next = None
        else:
            x.prev.next = x.next
            x.next.prev = x.prev

    def insert_before(self, x, item):
        """Insert an `item` before a given Node `x`."""
        if self._first is x:
            self.add_front(item)
        else:
            y = self._DoubleNode(item, next=x, prev=x.prev)
            x.prev.next = y
            x.prev = y

    def insert_after(self, x, item):
        """Insert an `item` after a given Node `x`."""
        if self._last is x:
            self.add_back(item)
        else:
            y = self._DoubleNode(item, next=x.next, prev=x)
            x.next.prev = y
            x.next = y

    def move_to_front(self, x):
        """Move a node to the front of the list."""
        if self._first is x:
            return
        if self._last is x:
            self._last = x.prev
        x.prev.next = x.next
        x.next.prev = x.prev
        x.next = self._first
        self._first.prev = x
        self._first = x
        x.prev = None

    def move_to_back(self, x):
        """Move a node to the back of the list."""
        if self._last is x:
            return
        if self._first is x:
            self._first = x.next
        x.prev.next = x.next
        x.next.prev = x.prev
        x.prev = self._last
        self._last.next = x
        self._last = x
        x.next = None

    def swap(self, a, b):
        """Swap the positions of nodes `a` and `b` in the list."""
        # Keep pointers to neighbors
        a_next = a.next
        a_prev = a.prev
        # connect a to b's neighbors
        a.next = b.next
        a.prev = b.prev
        if b.prev:
            b.prev.next = a
        else:
            self._first = a
        if b.next:
            b.next.prev = a
        else:
            self._last = a
        # connect b to a's neighbors
        b.next = a_next
        b.prev = a_prev
        if a_prev:
            a_prev.next = b
        else:
            self._first = b
        if a_next:
            a_next.prev = b
        else:
            self._last = b


if __name__ == "__main__":
    a = DoubleList('abcde')
    print(a)
    assert a._first.data == 'a'
    assert a._last.data == 'e'
    a.swap(a._first.next, a._last.prev)
    print(a)
    a.swap(a._first, a._last.prev)
    print(a)
    a.swap(a._last, a._first.next.next)
    print(a)

# =============================================================================
# =============================================================================
