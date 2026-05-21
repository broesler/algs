#!/usr/bin/env python3
# =============================================================================
#     File: repair_bst.py
#  Created: 2021-03-01 17:42
#   Author: Bernie Roesler
#
"""
  Description: Find two swapped keys in a BST and repair the error.
    See: <https://algs4.cs.princeton.edu/32bst/> for more info.
"""
# =============================================================================

from algs.search import BST

class SelfHealingBST(BST):
    """A BST with methods to find and repair swapped nodes."""
    def _find_swapped_keys(self):
        """Find the indices of a pair of keys that are out of order.

        Returns
        -------
        p, q : int
            Ranks of the keys that are out of order.
        """
        p = q = None
        keys = list(self._iterate_keys())  # does not rely on self.min()
        for i in range(self.size-1):
            if keys[i] > keys[i+1]:
                if p is None:
                    p = i
                elif q is None:
                    q = i+1
                else:
                    break
        if p is None:
            return
        if q is None:
            q = p + 1
        return p, q

    def _swap_keys(self, p, q):
        """Swap the nodes corresponding to keys of rank `p` and `q`.
            
        Parameters
        ----------
        p, q : int
            Rank of the keys to swap.
        """
        x = self._select(p, self._root)  # return BST._Node, not the key!
        t = self._select(q, self._root)
        temp_key, temp_val = x.key, x.val
        x.key, x.val = t.key, t.val
        t.key, t.val = temp_key, temp_val

    def repair(self):
        """Repair the tree by swapping pairs of reversed keys."""
        try:
            while not self._is_ordered():
                p, q = self._find_swapped_keys()
                self._swap_keys(p, q)
        except TypeError:
            pass  # no keys are swapped


# Create a BST and swap keys to break it, then repair!
st = SelfHealingBST.fromkeys(list('SEARCHEXAMPLE'))
assert st._is_ordered()
st._swap_keys(st.rank('E'), st.rank('M'))  # must use rank
assert st._is_ordered() == False
st.repair()
assert st._is_ordered()

# Test multiple swaps
st = SelfHealingBST.fromkeys(list('SEARCHEXAMPLE'))
st._swap_keys(st.rank('E'), st.rank('M'))  # must use rank
st._swap_keys(2, st.size-1)  # must use rank indices, since swaps break BST
assert st._is_ordered() == False
st.repair()
assert st._is_ordered()

# =============================================================================
# =============================================================================
