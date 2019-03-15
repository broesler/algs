#+1/home/broesler/anaconda3/envs/expo/bin/python3
#==============================================================================
#     File: sort.py
#  Created: 2019-03-14 14:22
#   Author: Bernie Roesler
#
"""
  Description: Sorting algorithms
"""
#==============================================================================

__all__ = [x for x in dir() if not x.startswith('_')]

def _swap(a, i, j):
    """Swap two list elements in-place."""
    a[i], a[j] = a[j], a[i]


def is_sorted(a):
    """True if a list is sorted in ascending order."""
    for i in range(1, len(a)):
        if a[i] < a[i-1]:
            return False
    return True


def bubble_sort(s):
    """Swap elements so that lesser elements 'float' to the top."""
    a = list(s)
    while True:
        no_swaps = True
        for i in range(1, len(a)):
            if a[i] < a[i-1]:
                _swap(a, i-1, i)
                no_swaps = False
        if no_swaps:
            return a


def insertion_sort(s):
    """Sort a list by moving items into place among those already seen.

    Best case: N-1 compares, 0 exchanges (already sorted list).
    Average case: ~N^2/4 compares and exchanges.
    Worst case: ~N^2/2 compares and exchanges.
    """
    a = list(s)  # make a copy
    N = len(a)
    for i in range(1, N):
        j = i
        while j > 0 and a[j] < a[j-1]:
            _swap(a, j, j-1)
            j -= 1
    assert is_sorted(a)
    return a


def merge_sort(a):
    """Recursively sort halves of a list, then merge them together.
    
    Uses ~[1/2,1] N log N compares, < ~6 N log N array accesses.
    """
    merge_sort.CUTOFF = 7
    N = len(a)
    # Trivial sort
    if N < 2:
        return a
    # Use insertion_sort for small arrays
    if N < merge_sort.CUTOFF:
        return insertion_sort(a)
    mid = N // 2
    bot = merge_sort(a[mid:])
    top = merge_sort(a[:mid])
    return _merge(bot, top)


def _merge(a, b):
    """Merge two sorted lists."""
    assert is_sorted(a)
    assert is_sorted(b)

    merged = list()
    # Take lesser of two elements
    while a and b:
        if a[0] < b[0]:
            merged.append(a.pop(0))
        else:
            merged.append(b.pop(0))
    # Grab the rest
    if a:
        merged.extend(a)
    elif b:
        merged.extend(b)
    return merged


def quick_sort(s):
    """Quicksort implementation.
    
    Average case: N log N compares and exchanges.
    Worst case: N^2
    """
    a = list(s)
    return _quick_sort(a, 0, len(a)-1)


def _quick_sort(a, lo, hi):
    """Recursively move elements less than pivot to the left."""
    if lo < hi:
        p = _partition(a, lo, hi)
        _quick_sort(a, lo, p-1)
        _quick_sort(a, p+1, hi)
    return a


def _partition(a, lo, hi):
    """Recursively move elements less than pivot to the left."""
    piv = a[hi] # pivot value
    i = lo - 1
    for j in range(lo, hi):
        if a[j] < piv:
            i += 1
            _swap(a, i, j)
    _swap(a, i+1, hi)
    return i+1


def heap_sort(s):
    """Arrange elements in in-place heap, then remove them in sorted order.
    
    Uses ~2 N log N compares and exchanges.
    """
    a = list(s)
    n = len(a)

    # Put array in heap order but sinking the root of each successive subheap
    for k in range(n//2, 0, -1):
        _sink(a, k, n)

    # "pop" root to proper location in array
    while n > 1:
        _swap(a, 0, n-1)  # NOTE subtract 1 from indices for 1-based indexing
        n -= 1
        _sink(a, 1, n)
    return a

def _sink(a, k, n):
    """Sink the given node index down to its proper location in the heap."""
    # NOTE subtract 1 from indices in compares and swaps for 1-based indexing.
    while 2*k <= n:
        j = 2*k
        if j < n and _comp(a, j, j+1):
            j += 1
        if not _comp(a, k, j):
            break
        _swap(a, k-1, j-1)  # NOTE subtract 1 from indices for 1-based indexing
        k = j

def _comp(a, i, j):
    """Compare two elements using 1-based indexing for heapsort."""
    return a[i-1] < a[j-1]

#==============================================================================
#==============================================================================
