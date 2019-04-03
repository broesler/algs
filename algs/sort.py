#!/usr/bin/env python3
#==============================================================================
#     File: sort.py
#  Created: 2019-03-14 14:22
#   Author: Bernie Roesler
#
"""
  Description: Sorting algorithms
"""
#==============================================================================

from random import randrange, shuffle

def _swap(a, i, j):
    """Swap two list elements in-place."""
    a[i], a[j] = a[j], a[i]


def is_sorted(a):
    """True if a list is sorted in ascending order."""
    for i in range(1, len(a)):
        if a[i-1] > a[i]:
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


def mergesort(a):
    """Recursively sort halves of a list, then merge them together.

    Uses ~[1/2, 1] N log N compares, < ~6 N log N array accesses.
    """
    mergesort.CUTOFF = 8
    N = len(a)
    # Trivial sort
    if N < 2:
        return a
    # Use insertion_sort for small arrays
    if N < mergesort.CUTOFF:
        return insertion_sort(a)
    mid = N // 2
    bot = mergesort(a[mid:])
    top = mergesort(a[:mid])
    return _merge(bot, top)


def mergesort_BU(a):
    """Sort pairs of log-scale growth subarrays.

    Uses ~[1/2, 1] N log N compares, < ~6 N log N array accesses.
    """
    N = len(a)
    out = list(a)  # return a copy
    slen = 1
    while slen < N:
        lo = 0
        while lo < (N - slen):
            mid = lo + slen
            hi = min(lo + 2*slen, N)
            # Place sorted pairs into output array
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


def quicksort0(s):
    """Quicksort implementation.

    Average case: ~ 2 N log N compares and ~ 1/3 N log N exchanges.
    Worst case: ~ N^2 / 2 compares if not randomized.

    WARNING: Goes O(N^2) for already-sorted keys
    WARNING: Goes O(N^2) for all equal keys
    """
    a = list(s)
    return _quicksort0(a, 0, len(a)-1)


def _quicksort0(a, lo, hi):
    """The actual quicksort algorithm."""
    if lo < hi:
        p = _partition0(a, lo, hi)
        _quicksort0(a, lo, p-1)
        _quicksort0(a, p+1, hi)
    return a


def _partition0(a, lo, hi):
    """Recursively move elements less than pivot to the left."""
    piv = a[hi]  # pivot value
    i = lo - 1
    for j in range(lo, hi):
        if a[j] < piv:
            i += 1
            _swap(a, i, j)
    _swap(a, i+1, hi)  # move pivot into position
    return i+1


def quicksort0r(s):
    """Quicksort implementation.
    Average case: ~ 2 N log N compares and ~ 1/3 N log N exchanges.
    WARNING: Goes O(N^2) for all equal keys
    """
    a = list(s)
    return _quicksort0r(a, 0, len(a)-1)


def _quicksort0r(a, lo, hi):
    """Recursively move elements less than pivot to the left."""
    if lo < hi:
        p = _partition0r(a, lo, hi)
        _quicksort0r(a, lo, p-1)
        _quicksort0r(a, p+1, hi)
    return a


def _partition0r(a, lo, hi):
    """Recursively move elements less than pivot to the left.
    Choose a random element as the pivot instead of shuffling the list.
    """
    idx = randrange(lo, hi+1)
    piv = a[idx]  # pivot value
    _swap(a, idx, hi)
    i = lo - 1
    for j in range(lo, hi):
        if a[j] < piv:
            i += 1
            _swap(a, i, j)
    _swap(a, i+1, hi)  # move pivot into position
    return i+1


#------------------------------------------------------------------------------ 
#        Engineering a Sorting Algorithm Examples
#------------------------------------------------------------------------------
def qsort0(s):
    """Quicksort implementation.

    Average case: ~ 2 N log N compares and ~ 1/3 N log N exchanges.
    Worst case: ~ N^2 / 2 compares if not randomized.

    WARNING: Goes O(N^2) for already-sorted keys
    WARNING: Goes O(N^2) for all equal keys
    """
    a = list(s)
    return _qsort0(a, 0, len(a)-1)


def _qsort0(a, lo, hi):
    """The actual quicksort algorithm."""
    if lo < hi:
        p = _part0(a, lo, hi)
        _qsort0(a, lo, p-1)
        _qsort0(a, p+1, hi)
    return a


def _part0(a, lo, hi):
    """A toy partition, not useful in practice due to O(N^2) worst-case."""
    j = lo  # j is boundary pointer
    for i in range(lo+1, hi+1):
        if (a[i] < a[lo]):
            j += 1
            _swap(a, i, j)
    _swap(a, lo, j)  # move pivot into position
    return j


def qsort1(s):
    """Quicksort implementation.

    Average case: ~2 N log N compares and ~1/3 N log N exchanges.

    WARNING: Goes O(N^2) for all equal keys
    """
    a = list(s)
    return _qsort1(a, 0, len(a)-1)


def _qsort1(a, lo, hi):
    """The actual quicksort algorithm."""
    if lo < hi:
        p = _part1(a, lo, hi)
        _qsort1(a, lo, p-1)
        _qsort1(a, p+1, hi)
    return a


def _part1(a, lo, hi):
    """Improved with randomization of the pivot."""
    i = lo
    j = hi
    idx = randrange(lo, hi+1)
    piv = a[idx]  # pivot value
    _swap(a, idx, lo)
    while True:
        i += 1
        while i < hi and a[i] < piv: i += 1
        while j > lo and a[j] > piv: j -= 1
        if j < i: 
            break
        _swap(a, i, j)

    _swap(a, lo, j)  # move pivot into position
    return j


def qsort2(s):
    """Bentley-McIlroy 3-way partitioning."""
    a = list(s)
    return _qsort2(a, 0, len(a)-1)


def _qsort2(a, lo, hi):
    # Use insertion_sort for small arrays
    # N = hi - lo + 1
    # _qsort2.CUTOFF = 8
    # if N < _qsort2.CUTOFF:
    #     return insertion_sort(a)

    if hi - lo > 1:
        p, q = _part2(a, lo, hi)
        _qsort2(a, lo, p)
        _qsort2(a, q, hi)
    return a


def _part2(a, lo, hi):
    """Partition s.t.:
        [ = ][   <   ][  ?  ][  >  ][ = ]
        lo   p        i      j      q    hi
    """
    # idx = randrange(lo, hi+1)
    idx = 0
    piv = a[idx]  # pivot value
    print(f"\nlo: {lo}, hi: {hi}, piv: {piv}")
    p = i = lo
    q = j = hi
    while True:
        print(f"{p:3d}  {i:3d}  {j:3d}  {q:3d}  {a}")
        # Scan pointers from each end
        while i <= j and a[i] <= piv:
            # Swap equal elements to left end
            if a[i] == piv:
                _swap(a, p, i)
                p += 1
            i += 1
        while j >= i and a[j] >= piv:
            # Swap equal elements to right end
            if a[j] == piv:
                _swap(a, j, q)
                q -= 1
            j -= 1

        # Pointers cross
        if j < i:
            break

        # Found out-of-order elements
        _swap(a, i, j)
        i += 1
        j -= 1


    # Move all elements equal to the pivot to the center
    print(f"{p:3d}  {i:3d}  {j:3d}  {q:3d}  {a}")
    print("Move to center...")
    i = j + 1
    for k in range(lo, p):
        _swap(a, k, j)
        j -= 1
    for k in range(hi, q, -1):
        _swap(a, k, i)
        i += 1
    print(f"{p:3d}  {i:3d}  {j:3d}  {q:3d}  {a}")
    return j, i  # role reversal


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
