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

from numpy.random import randint

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

    Uses ~[1/2, 1] N log N compares, < ~6 N log N array accesses.
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


def merge_sort_BU(a):
    """Sort pairs of log-scale growth subarrays.

    Uses ~[1/2, 1] N log N compares, < ~6 N log N array accesses.
    """
    N = len(a)
    out = list(a)
    slen = 1
    while slen < N:
        lo = 0
        while lo < (N - slen):
            mid = lo + slen
            hi = min(lo + 2*slen, N)
            out[lo:hi] = _merge(out[lo:mid], out[mid:hi])
            lo += 2*slen
        slen *= 2
    return out


def _merge(a, b):
    """Merge two sorted lists. Uses O(n) compares per item."""
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

    Average case: ~ 2 N log N compares and ~ 1/3 N log N exchanges.
    Worst case: ~ N^2 / 2 compares if not randomized.
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


# TODO implement 3-way partitioning (<, =, >)
def _partition(a, lo, hi):
    """Recursively move elements less than pivot to the left."""
    # idx = randint(lo, hi+1)
    # piv = a[idx]
    piv = a[hi] # pivot value
    i = lo - 1
    for j in range(lo, hi):
        if a[j] < piv:
            i += 1
            _swap(a, i, j)
    _swap(a, i+1, hi)
    return i+1


def heap_sort(s):
    """Arrange elements in in-place max-heap, then remove them in sorted order.

    Uses ~ 2 N log N compares and exchanges.
    """
    # NOTE subtract 1 from indices in `_swap` calls for 1-based indexing.
    a = list(s)
    N = len(a)

    # Put array in max-heap order
    for k in range(N//2, 0, -1):
        _sink(a, k, N)

    # heap is max-oriented, so "pop" root to end of array
    while N > 1:
        _swap(a, 0, N-1)
        N -= 1
        _sink(a, 1, N)
    return a


def _sink(a, k, N):
    """Sink the given node index down to its proper location in the heap."""
    # NOTE subtract 1 from indices in `_swap` calls for 1-based indexing.
    while 2*k <= N:
        j = 2*k
        if j < N and _comp(a, j, j+1):
            j += 1
        if not _comp(a, k, j):
            break
        _swap(a, k-1, j-1)
        k = j


def _comp(a, i, j):
    """Compare two elements in 1-based indexed max-heap."""
    return a[i-1] < a[j-1]

#==============================================================================
#==============================================================================
