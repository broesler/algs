#!/usr/bin/env python3
#==============================================================================
#     File: queue.py
#  Created: 2019-03-01 11:53
#   Author: Bernie Roesler
#
"""
  Description: Queue implementation
"""
#==============================================================================

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
        # _items[0] is "front" of queue
        self._items = list(items)

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
        return self._items.pop(0)

    def __iter__(self):
        yield from self._items

    def __bool__(self):
        return bool(self.size)

    def __repr__(self):
        return '<Queue: ' + self.__str__() + '>'

    def __str__(self):
        return str(self._items) 


if __name__ == '__main__':
    q = Queue(['A', 'B', 'C'])
    q.enqueue('D')
    assert q.size == 4
    assert not q.is_empty
    assert 'A' == q.peek()
    assert 'A' == q.dequeue()
    for c, item in zip(['B', 'C', 'D'], q):
        assert c == item

#==============================================================================
#==============================================================================
