#!/usr/bin/env python3
# =============================================================================
#     File: random_redblacks.py
#  Created: 2021-03-19 22:36
#   Author: Bernie Roesler
# =============================================================================

"""Exercise 3.3.17: Compare 2 random RedBlackBSTs with standard BSTs."""

import matplotlib.pyplot as plt
import numpy as np
from draw_tree import TreeArtist

from algs.search import BST, RedBlackBST

rng = np.random.default_rng(seed=565656)
N = 16  # number of nodes

fig = plt.figure(1, clear=True, constrained_layout=True)
gs = fig.add_gridspec(nrows=2, ncols=2)
for i in range(2):
    ax1 = fig.add_subplot(gs[i, 0])
    ax2 = fig.add_subplot(gs[i, 1], sharex=ax1, sharey=ax1)
    # ax2 = fig.add_subplot(gs[i, 1])

    if i == 0:
        ax1.set_title('Red-Black BST')
        ax2.set_title('BST')

    # Plot the BSTs
    keys = rng.random(size=N)
    drbst = TreeArtist(RedBlackBST.fromkeys(keys))
    dbst = TreeArtist(BST.fromkeys(keys))
    drbst.draw(ax=ax1, label_keys=False)
    dbst.draw(ax=ax2, label_keys=False)

gs.tight_layout(fig)
plt.show()
# =============================================================================
# =============================================================================
