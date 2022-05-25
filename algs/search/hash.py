#!/usr/bin/env python3
# =============================================================================
#     File: hash.py
#  Created: 2022-04-21 17:48
#   Author: Bernie Roesler
#
"""
  Description: Hash Tables.
"""
# =============================================================================

import numpy as np

from algs.search.table import SymbolTable, SequentialSearchST

__all__ = ['SeparateChainingHashST', 'SeparateChainingLiteHashST',
           'LinearProbingHashST', 'LazyLinearProbingHashST',
           'DoubleProbingHashST', 'DoubleHashingHashST', 'CuckooHashST']

# Table of primes less than the nearest power of 2
# Mersenne primes like 31 are nice because 31 = 2**5 - 1 == (1 << 5) - 1.
MIN_PRIMES = dict({
    2: 3,
    3: 7,
    4: 13,
    5: 31,
    6: 61,
    7: 127,
    8: 251,
    9: 509,
    10: 1021,
    11: 2039,
    12: 4093,
    13: 8191,
    14: 16381,
    15: 32749,
    16: 65521,
    17: 131071,
    18: 262139,
    19: 524287,
    20: 1048573,
    21: 2097143,
    22: 4194301,
    23: 8388593,
    24: 16777213,
    25: 33554393,
    26: 67108859,
    27: 134217689,
    28: 268435399,
    29: 536870909,
    30: 1073741789,
    31: 2147483647
})


# Define next prime after each power of 2
# MAX_PRIMES = dict({i: next_prime(2**i) for i in range(32)})
MAX_PRIMES = dict({
    0: 2,
    1: 3,
    2: 5,
    3: 11,
    4: 17,
    5: 37,
    6: 67,
    7: 131,
    8: 257,
    9: 521,
    10: 1031,
    11: 2053,
    12: 4099,
    13: 8209,
    14: 16411,
    15: 32771,
    16: 65537,
    17: 131101,
    18: 262147,
    19: 524309,
    20: 1048583,
    21: 2097169,
    22: 4194319,
    23: 8388617,
    24: 16777259,
    25: 33554467,
    26: 67108879,
    27: 134217757,
    28: 268435459,
    29: 536870923,
    30: 1073741827,
    31: 2147483659
})

MIN_CAPACITY = 5  # minimum number of hash slots


# -----------------------------------------------------------------------------
#         Functions
# -----------------------------------------------------------------------------
# See Exercise 3.4.23, 3.4.32
def java_hash(k, R=31):
    r"""Define the hash code function used by Java for strings.

    .. math::
        s_0 R^{N-1} + s_1 R^{N-2} + \dots + s_{N-1}

    See Also
    --------
    `Java standard: <https://docs.oracle.com/javase/6/docs/api/java/lang//String.html>`_
    """
    h = 0
    for c in k:
        h = (R * h) + ord(c)
    return h


def is_prime(n):
    """Returns True if `n` is prime."""
    # 0 and 1 are not prime, 2 is prime.
    if n <= 3:
        return n > 1
    # Cannot be divisible by 2 or 3
    if not n % 2 or not n % 3:
        return False
    # Check up to sqrt(n) for divisible factors
    i = 5
    while i < n**0.5:
        if not n % i or not n % (i + 2):
            return False
        i += 6
    return True


def next_prime(n):
    """Find the next prime number p > `n` >= 0."""
    if n < 0:
        raise ValueError(f"{n = } must be a postivie integer!")
    if n < 2:
        return 2
    # Start with the next odd number
    if (n+1) % 2 == 0:
        n += 1
    # Follow Bertrand's postulate for n > 1
    for i in range(n+1, 2*n+1, 2):
        if is_prime(i):
            return i
    else:
        return None


def prev_prime(n):
    """Find the previous prime number 2 <= p < `n`."""
    if n < 0:
        raise ValueError(f"{n = } must be a postivie integer!")
    if n < 2:
        return None
    # Start with the next odd number
    if (n-1) % 2 == 0:
        n -= 1
    for i in range(n-1, 2, -2):
        if is_prime(i):
            return i
    else:
        return None


# -----------------------------------------------------------------------------
#         Classes
# -----------------------------------------------------------------------------
class HashTable(SymbolTable):
    # An abstract implementation of a hash table
    def __init__(self, items=None, M=MIN_CAPACITY, resize=False):
        self.N = 0
        self.M = M
        self._RESIZE_FLAG = bool(resize)
        self._lgM = int(np.log2(self.M))
        super().__init__(items)

    __init__.__doc__ = (SymbolTable.__init__.__doc__ +
        """M : int, optional
            Minimum number of slots in the hash table.
        resize : bool, optional
            If True, resize the table by powers of 2 to maintain an average
            list length of `avg_probes`. Note that resizing changes the basic
            hash function to more evenly distribute the keys with a non-prime
            `M`.
        """)

    @property
    def size(self):
        return self.N

    @property
    def _load_factor(self):
        """Return the ratio of items in the table to the number of slots."""
        return self.N / self.M

    def _hash(self, k):
        """Return an integer hash code for the key `k`.

        To be a proper hash function, the returned value must be:
            - deterministic: if key_a == key_b, then hash(key_a) == hash(key_b)
            - efficient to compute
            - uniformly distribute the keys across `M` slots in the table.

        .. note:: built-in `hash` is "salted" each time python is run for
        security reasons, so results are non-deterministic.
        """
        t = hash(k)
        # Exercise 3.4.18 (see Q&A p 478)
        # Ensure even distribution when M is power of 2
        if self._RESIZE_FLAG and self._lgM < 26:
            t = t % MIN_PRIMES[self._lgM + 5]
        return t % self.M


class SeparateChainingHashST(HashTable):
    __doc__ = f"""Implements a hash table with separate chaining.
               {SymbolTable.__doc__}"""

    def __init__(self, items=None, M=MIN_CAPACITY, resize=False,
                 avg_probes=10, cache=False):
        self._AVG_PROBES = avg_probes  # maximum average list size
        assert self._AVG_PROBES > 0
        # Initialize the actual symbol table
        self._st = [SequentialSearchST() for _ in range(M)]
        super().__init__(items=items, M=M, resize=resize)

    __init__.__doc__ = (HashTable.__init__.__doc__ +
        """avg_probes : int > 0, optional
            Desired average table size. If `resize` is True, the table size `M`
            will be adjusted such that `N/M` ~ `avg_probes` as keys are added
            or deleted.
        """)

    def _validate_size(self):
        assert self.size == sum(self._list_lengths())

    def _list_lengths(self):
        return [t.size for t in self._st]

    def _resize(self, M):
        """Resize the array of hash slots."""
        # Create a new table and hash the existing keys into it
        t = self.__class__(self.items(), M=M, resize=True)
        # Use the new table in *self*
        self._st = t._st
        self.M = t.M

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
        # Double table size if average list length >= AVG_PROBES (e.g. 10)
        if self._RESIZE_FLAG and self.N >= self._AVG_PROBES*self.M:
            self._resize(2*self.M)
            self._lgM += 1
        t = self._st[self._hash(k)]
        if k not in t:
            self.N += 1
        t[k] = v
        self._cost = 1 + t._cost

    def __getitem__(self, k):
        t = self._st[self._hash(k)]
        try:
            v = t[k]
            self._cost = 1 + t._cost
        except KeyError:
            self._cost = 1 + t._cost
            raise KeyError(k)
        return v

    # Exercise 3.4.9, eager delete
    def __delitem__(self, k):
        t = self._st[self._hash(k)]
        try:
            del t[k]
            self.N -= 1
            self._cost = 1 + t._cost
        except KeyError:
            self._cost = 1 + t._cost
            raise KeyError(k)
        # Halve table size if average list length <= 2
        if (self._RESIZE_FLAG and
                self.M > MIN_CAPACITY and self.N <= 2*self.M):
            self._resize(self.M // 2)
            self._lgM -= 1

    # -------------------------------------------------------------------------
    #         Iterator functions
    # -------------------------------------------------------------------------
    def _make_iterator(self, rtype):
        """Return an iterator over all of the items in the table."""
        def iterator(self):
            """Iterate over each symbol table."""
            q = list()
            for t in self._st:
                q.extend(t.keys() if rtype == 'keys' else
                         (t.values() if rtype == 'values' else t.items()))
            return q
        return iterator

    def __str__(self):
        """Overrides `SymbolTable`."""
        out = ''
        for i, t in enumerate(self._st):
            out += f"[{i}]: {repr(t)}\n"
        return out

    def __repr__(self):
        """Overrides `SymbolTable`."""
        return f"<{self.__class__.__name__}:\n{self.__str__()}>"

    # -------------------------------------------------------------------------
    #         Exercises
    # -------------------------------------------------------------------------
    # Exercise 3.4.30
    def chi_square(self):
        r"""The χ² statistic for the hash table.

        The statistic is defined by:

        .. math::
            \chi^2 = \frac{M}{N} ( (f_0 - \frac{N}{M})^2
                + (f_1 - \frac{N}{M})^2 + \dots (f_{M-1} - \frac{N}{M})^2 )

        where :math:`f_i` is the number of keys with hash value :math:`i`.
        For :math:`N > cM`, the statistic should be :math:`M \pm \sqrt{M}` with
        probability :math:`1 - 1/c`.

        The statistic will be distributed ~ χ² with *M-2* degrees of freedom.
        """
        alpha = self.N / self.M  # typically > 1
        table_lens = np.r_[[t.size for t in self._st]]
        return np.sum((table_lens - alpha)**2) / alpha


# Exercise 3.4.2
class SeparateChainingLiteHashST(HashTable):
    __doc__ = f"""Implements a hash table with separate chaining, but uses
        a nested linked list insteady of `ArrayST` dependency.
        {SymbolTable.__doc__}"""

    # Private class of key/value pairs
    class _Node():
        """Internal item object to hold key and value."""
        def __init__(self, key, value, next=None, N_before=0):
            self.key = key
            self.val = value
            self.N_before = N_before  # entries in table when Node created
            self.next = next

        def __str__(self):
            return f"({repr(self.key)}: {repr(self.val)})"

        def __repr__(self):
            return f"<{self.__class__.__name__}: {self.__str__()}>"

    def __init__(self, items=None, M=MIN_CAPACITY, resize=False,
                 avg_probes=10, cache=False):
        self._AVG_PROBES = avg_probes  # desired average list size
        assert self._AVG_PROBES > 0
        # Initialize the symbol table
        self._st = M*[None]   # Create M linked lists
        super().__init__(items=items, M=M, resize=resize)

    __init__.__doc__ = SeparateChainingHashST.__init__.__doc__

    _resize = SeparateChainingHashST._resize

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
        # Double table size if average list length >= 10
        if self._RESIZE_FLAG and self.N >= self._AVG_PROBES*self.M:
            self._resize(2*self.M)
            self._lgM += 1

        # Hash into table
        i = self._hash(k)
        x = self._st[i]
        self._cost = 1

        if x is None:
            # Create new linked list at hash table location
            self._st[i] = self._Node(k, v, N_before=self.N)
            self.N += 1
            return

        # There is a hash collision. Search for key.
        while x:
            if k == x.key:
                x.val = v
                return
            else:
                x = x.next
                self._cost += 1
        else:
            # Insert new node at beginning of list
            self._st[i] = self._Node(k, v, self._st[i], N_before=self.N)
            self.N += 1

    def __getitem__(self, k):
        x = self._st[self._hash(k)]
        self._cost = 1
        while x:
            if k == x.key:
                return x.val
            else:
                x = x.next
                self._cost += 1
        else:
            raise KeyError(k)

    def __delitem__(self, k):
        i = self._hash(k)
        self._cost = 1
        x = self._st[i]
        if x is None:
            raise KeyError(k)

        # Check the first node
        if k == x.key:
            self._st[i] = x.next
            self.N -= 1
            return

        while x.next:
            if k == x.next.key:
                x.next = x.next.next  # unlink the node
                self.N -= 1
                return
            else:
                x = x.next
                self._cost += 1
        else:
            raise KeyError(k)

        # Halve table size if average list length <= 2
        if (self._RESIZE_FLAG and
                self.M > MIN_CAPACITY and self.N <= 2*self.M):
            self._resize(self.M // 2)
            self._lgM -= 1

    # Exercise 3.4.3
    def delete_later_than(self, k):
        """Delete all entries in the table that were inserted after `k`."""
        for i in range(self.M):
            if self._st[i] is None:
                continue
            # Larger numbers will always be at the front of the table given our
            # insert-at-front algorithm. Keep deleting from front.
            x = self._st[i]
            while x:
                if x.N_before > k:
                    self._st[i] = x.next
                    self.N -= 1
                x = x.next

    # -------------------------------------------------------------------------
    #         Iteration
    # -------------------------------------------------------------------------
    def _nodes(self):
        return self._make_iterator(rtype='nodes')(self)

    # Exercise 3.4.19
    def _make_iterator(self, rtype):
        def iterator(self):
            """Iterate over each symbol table."""
            q = list()
            for t in self._st:
                x = t
                while x:
                    q.append(x.key if rtype == 'keys' else
                             (x.val if rtype == 'values' else
                             (x.key, x.val) if rtype == 'items' else x))
                    x = x.next
            return q
        return iterator

    def __str__(self):
        """Overrides `SymbolTable`."""
        out = ''
        for i, t in enumerate(self._st):
            x = t
            out += f"[{i}]: ["
            while x:
                out += str(x)
                if x.next:
                    out += ", "
                x = x.next
            out += "]\n"
        return out

    def __repr__(self):
        """Overrides `SymbolTable`."""
        return f"<{self.__class__.__name__}:\n{self.__str__()}>"


# Exercise 3.4.27
class DoubleProbingHashST(SeparateChainingHashST):
    __doc__ = f"""Implements a hash table with separate chaining, but uses two
               hash functions to double probe.
               {SymbolTable.__doc__}"""

    # NOTE resizing not yet supported

    def _hash_b(self, k):
        """Return an integer hash code for the key `k` that is distinct from
        that of `HashTable._hash`.
        """
        return (31 * self._hash(k)) % self.M

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
        # Hash into 2 lists and choose the shorter
        ta = self._st[self._hash(k)]
        tb = self._st[self._hash_b(k)]
        if k in ta:
            ta[k] = v
            self._cost = 2 + ta._cost  # assume "caching"
        elif k in tb:
            tb[k] = v
            self._cost = 2 + ta._cost + tb._cost
        else:
            self.N += 1
            t = ta if len(ta) < len(tb) else tb  # choose the shorter list
            t[k] = v
            self._cost = 2 + ta._cost + tb._cost + t._cost

    def __getitem__(self, k):
        # Hash into 2 lists and search for key in each
        ta = self._st[self._hash(k)]
        tb = self._st[self._hash_b(k)]
        if k in ta:
            v = ta[k]
            self._cost = 2 + ta._cost
        elif k in tb:
            v = tb[k]
            self._cost = 2 + ta._cost + tb._cost
        else:
            self._cost = 2 + ta._cost + tb._cost
            raise KeyError(k)
        return v

    def __delitem__(self, k):
        # Hash into 2 lists and search for key in each
        ta = self._st[self._hash(k)]
        tb = self._st[self._hash_b(k)]
        self._cost = 2
        if k in ta:
            del ta[k]
            self._cost = 2 + ta._cost
        elif k in tb:
            del tb[k]
            self._cost = 2 + ta._cost + tb._cost
        else:
            self._cost = 2 + ta._cost + tb._cost
            raise KeyError(k)
        self.N -= 1


class LinearProbingHashST(HashTable):
    __doc__ = f"""Implements a hash table using arrays with linear probing.
                {SymbolTable.__doc__}"""

    def __init__(self, items=None, M=MIN_CAPACITY, resize=True, cache=False):
        # Initialize the symbol table
        self._keys = M*[None]
        self._vals = M*[None]
        super().__init__(items=items, M=M, resize=resize)

    def _resize(self, M):
        """Resize the internal keys and values arrays."""
        # Create a new table and hash the existing keys into it
        t = self.__class__(M=M, resize=True)
        for k, v in zip(self._keys, self._vals):
            if k is not None:
                t[k] = v
        # Use those new arrays in *self*
        self._keys = t._keys
        self._vals = t._vals
        self.M = t.M

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
        if not self._RESIZE_FLAG and self.N == self.M:
            raise RuntimeError(("Trying to insert into a full table! "
                                "Set `resize=True`."))

        if self._RESIZE_FLAG and self.N >= self.M // 2:
            self._resize(2*self.M)
            self._lgM += 1

        i = self._hash(k)
        self._cost = 1
        while self._keys[i] is not None:
            if k == self._keys[i]:
                self._vals[i] = v
                return
            else:
                i = (i + 1) % self.M
                self._cost += 1
        else:
            self._keys[i] = k
            self._vals[i] = v
            self.N += 1

    def __getitem__(self, k):
        i = self._hash(k)
        self._cost = 1
        while self._keys[i] is not None:
            if k == self._keys[i]:
                return self._vals[i]
            else:
                i = (i + 1) % self.M
                self._cost += 1
        else:
            raise KeyError(k)

    def __delitem__(self, k):
        if k not in self:
            raise KeyError(k)
        i = self._hash(k)
        _cost = 1
        # Set slot of `k` to None
        while k is not self._keys[i]:
            i = (i + 1) % self.M
            _cost += 1
        self._keys[i] = None
        self._vals[i] = None
        i = (i + 1) % self.M
        # Rehash all keys in the cluster to the right of the deleted key
        while self._keys[i] is not None:
            key_to_redo = self._keys[i]
            val_to_redo = self._vals[i]
            self._keys[i] = None
            self._vals[i] = None
            self.N -= 1
            self.__setitem__(key_to_redo, val_to_redo)
            i = (i + 1) % self.M
            _cost += self._cost  # self._cost updated in __setitem__
        self.N -= 1
        self._cost = _cost
        # Check for a resize if table is small enough
        if self._RESIZE_FLAG and (self.N > 0 and self.N <= self.M // 8):
            self._resize(self.M // 2)
            self._lgM -= 1

    # -------------------------------------------------------------------------
    #         Iterators
    # -------------------------------------------------------------------------
    def keys(self):
        return [k for k in self._keys if k is not None]

    def values(self):
        return [v for (k, v) in zip(self._keys, self._vals) if k is not None]

    def items(self):
        return [(k, v) for (k, v) in zip(self._keys, self._vals)
                if k is not None]

    # -------------------------------------------------------------------------
    #         Exercises
    # -------------------------------------------------------------------------
    # Exercise 3.4.20
    def cost_of_hit(self):
        r"""Average cost of a search *hit* in the table.

        .. note::
            Probability theory gives :math:`1/2 (1 + 1/(1 - \alpha))`.[0]

        .. [0]:: Sedgewick, p 473.
        """
        return 1 + np.sum(self._hash_displacements()) / self.N

    def _hash_displacements(self):
        """Compute the distance of each key from its hash location."""
        return [(self._get_index(k) - self._hash(k)) % self.M
                for k in self.keys()]

    def _get_index(self, k):
        """Return the internal index of `k`."""
        i = self._hash(k)
        while self._keys[i] is not None:
            if k == self._keys[i]:
                return i
            else:
                i = (i + 1) % self.M
        else:
            raise KeyError(k)

    # Exercise 3.4.21
    def cost_of_miss(self):
        r"""Average cost of a search *miss* in the table.[0]

        .. note::
            Probability theory gives :math:`1/2 (1 + 1/(1 - \alpha)^2)`.[0]
            Cost of cluster length :math:`t` is :math:`\frac{t(t+1)}{2M}`.

        .. [0]:: Sedgewick, p 473.
        """
        return 1 + ((self.N + np.sum(np.r_[self._cluster_lengths()]**2))
                    / (2*self.M))

    def _cluster_lengths(self):
        """Compute the lengths of each cluster of keys in the table."""
        # Check if table is full
        if self.N == self.M:
            return [self.N]

        # Find first null slot so we can count wrap-around index as one cluster
        lo = 0
        for k in self._keys:
            if k is None:
                break
            lo += 1

        # Count the cluster lengths
        clusters = list()
        i = lo + 1
        t = 0
        while True:
            # Reset counter at new cluster
            if self._keys[i] is None:
                if t != 0:
                    clusters.append(t)
                    t = 0
            else:
                t += 1

            # Increment and check for wrap-around finish
            i = (i + 1) % self.M
            if i == lo + 1:
                break

        return clusters


# Exercise 3.4.26
class LazyLinearProbingHashST(LinearProbingHashST):
    __doc__ = f"""Implements a hash table using arrays with linear probing, but
                performs delete lazily, only removing keys on resize.
                {SymbolTable.__doc__}"""

    # NOTE the `fromkeys` class method will fail with this class since `None`
    # is used as a sentinel, and the default `value=None`.

    def _resize(self, M):
        """Resize the internal keys and values arrays."""
        # Create a new table and hash the existing keys into it
        t = self.__class__(M=M, resize=True)
        for k, v in zip(self._keys, self._vals):
            # Do not copy keys if value is None == "deletion"
            if k is not None and v is not None:
                t[k] = v
        # Use those new arrays in *self*
        self._keys = t._keys
        self._vals = t._vals
        self.M = t.M

    def __getitem__(self, k):
        i = self._hash(k)
        self._cost = 1
        while self._keys[i] is not None:
            # None marks "deleted" keys
            if k == self._keys[i] and self._vals[i] is not None:
                return self._vals[i]
            else:
                i = (i + 1) % self.M
                self._cost += 1
        else:
            raise KeyError(k)

    def __delitem__(self, k):
        if k not in self:
            raise KeyError(k)
        i = self._hash(k)
        self._cost = 1
        # Set *value* slot of `k` to None, but leave *key* in place
        while k is not self._keys[i]:
            i = (i + 1) % self.M
            self._cost += 1
        self._vals[i] = None
        # Do *not* rehash the keys in the cluster! We're being lazy.
        self.N -= 1  # count this as a deletion
        # Check for a resize if table is small enough
        if self._RESIZE_FLAG and (self.N > 0 and self.N <= self.M // 8):
            self._resize(self.M // 2)
            self._lgM -= 1

    # -------------------------------------------------------------------------
    #         Iterators
    # -------------------------------------------------------------------------
    def keys(self):
        return [k for (k, v) in zip(self._keys, self._vals)
                if k is not None and v is not None]

    def values(self):
        return [v for (k, v) in zip(self._keys, self._vals)
                if k is not None and v is not None]

    def items(self):
        return [(k, v) for (k, v) in zip(self._keys, self._vals)
                if k is not None and v is not None]


# Exercise 3.4.28
class DoubleHashingHashST(LinearProbingHashST):
    __doc__ = f"""Implements a hash table using arrays with linear probing, but
                uses a second hash function to define the probe sequence.
                {SymbolTable.__doc__}"""

    # NOTE we guarantee M to be prime in this class, so no need to re-mod the
    # hash code to a prime number.

    def _hash(self, k):
        """Return an integer hash code for the key `k`."""
        return hash(k) % self.M

    def _hash_b(self, k):
        """Return a key-dependent, non-zero integer to define the probe
        sequence."""
        R = MIN_PRIMES[self._lgM]  # NOTE `R` must be prime < self.M
        return R - (hash(k) % R)

    # -------------------------------------------------------------------------
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
        if not self._RESIZE_FLAG and self.N == self.M:
            raise RuntimeError(("Trying to insert into a full table! "
                                "Set `resize=True`."))

        if self._RESIZE_FLAG and self.N >= self.M // 2:
            # "double" the table size to the prime > the next power of 2
            self._lgM += 1
            self._resize(MAX_PRIMES[self._lgM])

        i = self._hash(k)
        x = self._hash_b(k)
        self._cost = 2
        while self._keys[i] is not None:
            if k == self._keys[i]:
                self._vals[i] = v
                return
            else:
                i = (i + x) % self.M
                self._cost += 1
        else:
            self._keys[i] = k
            self._vals[i] = v
            self.N += 1

    def __getitem__(self, k):
        i = self._hash(k)
        x = self._hash_b(k)
        self._cost = 2
        while self._keys[i] is not None:
            if k == self._keys[i]:
                return self._vals[i]
            else:
                i = (i + x) % self.M
                self._cost += 1
        else:
            raise KeyError(k)

    def __delitem__(self, k):
        if k not in self:
            raise KeyError(k)
        i = self._hash(k)
        x = self._hash_b(k)
        _cost = 2
        # Set slot of `k` to None
        while k is not self._keys[i]:
            i = (i + x) % self.M
            _cost += 1
        self._keys[i] = None
        self._vals[i] = None
        i = (i + x) % self.M
        # Rehash all keys in the cluster to the right of the deleted key
        while self._keys[i] is not None:
            key_to_redo = self._keys[i]
            val_to_redo = self._vals[i]
            self._keys[i] = None
            self._vals[i] = None
            self.N -= 1
            self.__setitem__(key_to_redo, val_to_redo)
            i = (i + x) % self.M
            _cost += self._cost  # self._cost updated in __setitem__
        self.N -= 1
        self._cost = _cost
        # Check for a resize if table is small enough
        if self._RESIZE_FLAG and (self.N > 0 and self.N <= self.M // 8):
            self._lgM -= 1
            self._resize(MAX_PRIMES[self._lgM])


# Exercise 3.4.31
# TODO Try implementing with a single table, where hashes go to different
# locations in the table like DoubleHashingHashST.
class CuckooHashST(HashTable):
    __doc__ = f"""Implements a hash table using two arrays with two hashes.
                {SymbolTable.__doc__}"""

    # -------------------------------------------------------------------------
    #         Internal tables
    # -------------------------------------------------------------------------
    class HashArrayA():
        """A local container class."""
        def __init__(self, M):
            self.keys = M*[None]
            self.vals = M*[None]
            self.M = M
            self.N = 0

        _load_factor = HashTable._load_factor

        def hash(self, k):
            return hash(k) % self.M

        def __str__(self):
            return str(list(zip(self.keys, self.vals)))

        __repr__ = SymbolTable.__repr__

    class HashArrayB(HashArrayA):
        """A local container class with a distinct hash function."""
        def hash(self, k):
            return (31 * hash(k)) % self.M

    # ------------------------------------------------------------------------- 
    #         Initialize
    # -------------------------------------------------------------------------
    def __init__(self, items=None, M=MIN_CAPACITY, resize=True, cache=False):
        self._ta = self.HashArrayA(M)
        self._tb = self.HashArrayB(M)
        super().__init__(items=items, M=M, resize=resize)
        self.M = self._ta.M + self._tb.M  # may be wrong without resizing

    @property
    def _keys(self):
        return self._ta.keys + self._tb.keys

    @property
    def _vals(self):
        return self._ta.vals + self._tb.vals

    def _validate_size(self):
        assert self.size == (self._ta.N + self._tb.N)

    def _resize(self, M):
        """Resize the internal tables."""
        # Create a new table and hash the existing keys into it
        t = self.__class__(M=M, resize=True)
        for k, v in zip(self._keys, self._vals):
            if k is not None:
                t[k] = v
        # Use those new tables in *self*
        self._ta = t._ta
        self._tb = t._tb
        self.M = self._ta.M + self._tb.M

    def _rehash(self):
        """Choose new hash functions? And rebuild the data structure."""
        pass

    # ------------------------------------------------------------------------- 
    #         Public API
    # -------------------------------------------------------------------------
    def __setitem__(self, k, v):
        self._cost = 0
        self._set(k, v)

    def _set(self, k, v, depth=0):
        if (not self._RESIZE_FLAG and
                ((self._ta.N == self._ta.M) or
                 (self._tb.N == self._tb.M))):
            raise RuntimeError(("Trying to insert into a full table! "
                                "Set `resize=True`."))

        if (self._RESIZE_FLAG and
                ((self._ta.N >= self._ta.M // 2) or
                 (self._tb.N >= self._tb.M // 2))):
            self._lgM += 1
            self._resize(MAX_PRIMES[self._lgM])

        # See Pagh and Rodler, 3.1.2
        if np.isclose(self._ta._load_factor, 0):
            _MAX_ITER = 1
        else: 
            _MAX_IDEAL = 3 * np.log(self.N) / np.log(1 + self._ta._load_factor)
            _MAX_ITER = int(np.max([1, _MAX_IDEAL]))

        c = 0
        while c < _MAX_ITER:
            # Hash into table A
            i = self._ta.hash(k)
            xk, xv = self._ta.keys[i], self._ta.vals[i]
            self._cost += 1
            if k == xk:
                self._ta.vals[i] = v
                return
            else:
                # put the new key/value in table A
                self._ta.keys[i] = k
                self._ta.vals[i] = v
                # If it's the first time through, we're adding a new key
                if c == 0:
                    self.N += 1

            # If the existing slot was empty, we're done
            if xk is None:
                self._ta.N += 1
                return

            # Hash collision: hash into table B with xk
            i = self._tb.hash(xk)
            yk, yv = self._tb.keys[i], self._tb.vals[i]
            self._cost += 1
            if xk == yk:
                raise RuntimeError(("Table is inconsistent! "
                                    f"Two instances of k = {xk}"))
            else:
                # move the existing key `xk` into the table B
                self._tb.keys[i] = xk
                self._tb.vals[i] = xv

            # If the existing slot was empty, we're done
            if yk is None:
                self._tb.N += 1
                return
            else:
                # repeat cycle with the next key/value pair
                k, v = yk, yv
                c += 1
        else:
            self._rehash()
            self._set(k, v, depth=depth+1)

    def __getitem__(self, k):
        t = self._ta
        # Hash into table A first
        i = t.hash(k)
        self._cost = 1
        if k == t.keys[i]:
            return t.vals[i]

        # if key is not there, hash into table B
        t = self._tb
        i = t.hash(k)
        self._cost = 2
        if k == t.keys[i]:
            return t.vals[i]
        else:
            raise KeyError(k)

    def __delitem__(self, k):
        # Hash into table A first
        t = self._ta
        i = t.hash(k)
        self._cost = 1
        if k == t.keys[i]:
            t.keys[i] = None
            t.vals[i] = None
        else:
            # if key is not there, hash into table B
            t = self._tb
            i = t.hash(k)
            self._cost = 2
            if k == t.keys[i]:
                t.keys[i] = None
                t.vals[i] = None
            else:
                raise KeyError(k)

        # track key counts
        t.N -= 1
        self.N -= 1

        # Check for a resize if table is small enough
        if (self._RESIZE_FLAG and
                ((self._ta.N > 0 and self._ta.N <= self._ta.M // 8) or
                 (self._tb.N > 0 and self._tb.N <= self._tb.M // 8))):
            self._lgM -= 1
            self._resize(MAX_PRIMES[self._lgM])

    # ------------------------------------------------------------------------- 
    #         Iterators
    # -------------------------------------------------------------------------
    def keys(self):
        return [k for k in self._keys if k is not None]

    def values(self):
        return [v for (k, v) in zip(self._keys, self._vals) if k is not None]

    def items(self):
        return [(k, v) for (k, v) in zip(self._keys, self._vals)
                if k is not None]


# -----------------------------------------------------------------------------
#         Run tests
# -----------------------------------------------------------------------------
# TODO move to unit tests test_hash.py
if __name__ == '__main__':
    # Exercise 3.4.1
    keys = 'EASYQUTION'
    items = [(c, i) for i, c in enumerate(keys)]

    def _hash_code(k, R=11):
        return R*(ord(k) - ord('A'))

    def _hash(self, k, **kwargs):
        return _hash_code(k, **kwargs) % self.M

    # Override _hash function with custom subclass
    class MySeparateChainingHashST(SeparateChainingHashST):
        _hash = _hash

    st = MySeparateChainingHashST(items, M=5)
    st._validate_size()
    assert st.keys() == list('UAQNISOTYE')

    try:
        del st['X']
    except KeyError:
        pass
    assert st._cost == 4  # _hash('X') == 3, len(st[3]) == 3 + 1 = 4

    # Repeat with SeparateChainingLiteHashST
    class MySeparateChainingLiteHashST(SeparateChainingLiteHashST):
        _hash = _hash

    stl = MySeparateChainingLiteHashST(items, M=5)
    assert stl.keys() == list('UAQNISOTYE')

    # Exercise 3.4.3
    stl.delete_later_than(5)  # corresponds to 'U'
    assert all([x.N_before <= 5 for x in stl._nodes()])
    assert all([k in list('EASYQU') for k in stl.keys()])

    # Exercise 3.4.10 (a)
    # Override _hash function with custom subclass
    class MyLinearProbingHashST(LinearProbingHashST):
        _hash = _hash

        # overwrite _resize to print _keys for visualization
        def _print_keys(func):
            def wrapper(self, *args, **kwargs):
                print(f"M = {self.M:2d}: {self._keys}")
                func(self, *args, **kwargs)
            return wrapper

        @_print_keys
        def _resize(self, M):
            super()._resize(M)

    sta = MyLinearProbingHashST(items, M=16, resize=False)
    assert sta.keys() == list('AQTSYIOEUN')
    assert np.allclose(sta._cluster_lengths(), [1, 3, 2, 4])

    # Exercise 3.4.10 (b)
    stb = MyLinearProbingHashST(items, M=10, resize=False)
    assert stb.keys() == list('AUINEYQOST')
    assert np.allclose(stb._cluster_lengths(), [10])

    # Exercise 3.4.11
    stc = MyLinearProbingHashST(items, M=4, resize=True)
    print(f"M = {stc.M:2d}: {stc._keys}")
    assert stc.keys() == list('ASYENQTIOU')

    # Exercise 3.4.27
    class MyDoubleProbingHashST(DoubleProbingHashST):
        _hash = _hash  # R = 11

        def _hash_b(self, k):
            return self._hash(k, R=7)

    std = MyDoubleProbingHashST(items, M=3)
    assert std.keys() == list('YSANOTEIUQ')

    # Exercise 3.4.28
    class MyDoubleHashingHashST(DoubleHashingHashST):
        _hash = _hash  # R = 11

        def _hash_b(self, k):
            return (self._hash(k, R=17) % self.M) + 1  # must be non-zero

    ste = MyDoubleHashingHashST(items, M=11)
    assert ste.keys() == list('AYOESITQNU')

    stf = CuckooHashST(items, M=23)

    keys = 'SEARCHEXAMPLE'
    items = [(c, i) for i, c in enumerate(keys)]
    stg = CuckooHashST(items)


# =============================================================================
# =============================================================================
