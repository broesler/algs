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
           'LinearProbingHashST', 'DoubleProbingHashST', 'DoubleHashingHashST']

# Table of primes less than the nearest power of 2
# Mersenne primes like 31 are nice because 31 = 2**5 - 1 == (1 << 5) - 1.
PRIMES = dict({
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


MIN_CAPACITY = 5  # minimum number of hash slots


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
            t = t % PRIMES[self._lgM + 5]
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
        t = self.__class__(self.items(), M=M)
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
        v = t[k]
        self._cost = 1 + t._cost
        return v

    # Exercise 3.4.9, eager delete
    def __delitem__(self, k):
        t = self._st[self._hash(k)]
        if k in t:
            self.N -= 1
        del t[k]
        self._cost = 1 + t._cost
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
        self._cost = 2
        if k in ta:
            ta[k] = v
            self._cost += ta._cost
        elif k in tb:
            tb[k] = v
            self._cost += tb._cost
        else:
            self.N += 1
            t = ta if len(ta) < len(tb) else tb  # choose the shorter list
            t[k] = v
            self._cost += t._cost


    def __getitem__(self, k):
        # Hash into 2 lists and search for key in each
        ta = self._st[self._hash(k)]
        tb = self._st[self._hash_b(k)]
        self._cost = 2

        try:
            return self._get(k, ta)
        except KeyError:
            pass

        try:
            return self._get(k, tb)
        except KeyError:
            raise KeyError(k)

    def _get(self, k, t):
        """Get the value associated with `k` from a sub-table `t`."""
        v = t[k]
        self._cost += t._cost
        return v


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
        t = self.__class__(M=M)
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
        if not self.__contains__(k):
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


# Exercise 3.4.28
class DoubleHashingHashST(LinearProbingHashST):
    __doc__ = f"""Implements a hash table using arrays with linear probing, but
                uses a second hash function to define the probe sequence.
                {SymbolTable.__doc__}"""

    # NOTE this class assumes that `M` is prime. If M is not prime, we may get
    # stuck in an infinite loop where we never find an empty slot.
    # TODO guarantee size of table is prime. Use dictionary similar to
    # `PRIMES`, but with primes *greater* than the powers of 2, so we always
    # have a slightly too-large table. We could also then eliminate the extra
    # mod operation in `_hash` and use `hash(k) % M` directly.

    def _hash_b(self, k):
        """Return a non-zero integer to define the probe sequence."""
        return 31 - (hash(k) % 31)

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
    assert ste.keys() == list('EATQIUYNOS')


# =============================================================================
# =============================================================================
