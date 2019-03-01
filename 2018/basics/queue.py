#!/home/broesler/anaconda3/envs/expo/bin/python3
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
    *items : list
        List of items to add to the queue, in FIFO order.

    Attributes
    ----------
    size : int
        Number of items in queue.
    is_empty : bool
        True if `size == 0`
    """
    def __init__(self, *items):
        self._items = list(items)

    @property
    def size(self):
        return len(self._items)

    @property
    def is_empty(self):
        return (self.size == 0)

    def peek(self):
        """Look at first item in queue."""
        return self._items[0]

    def enqueue(self, item):
        """Add item to the end of the queue.

        Parameters
        ----------
        item : object
            Item to add to the queue.
        """
        self._items.append(item)

    def dequeue(self):
        """Remove item from the front of the queue.

        Returns
        -------
        result : object
            First item added to the queue.
        """
        return self._items.pop(0)

    def __iter__(self):
        for item in self._items:
            yield item

    def __str__(self):
        return ' '.join([str(x) for x in self._items])


if __name__ == '__main__':
    from basics.queue import Queue
    q = Queue(*[1, 2, 3])
    assert q.size == 3
    assert not q.is_empty
    q.enqueue(4)
    # Test iteration
    for item in q:
        print(item)

#==============================================================================
#==============================================================================
