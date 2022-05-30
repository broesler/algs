#!/usr/bin/env python3
# =============================================================================
#     File: erdos_renyi_costs.py
#  Created: 2022-05-30 18:38
#   Author: Bernie Roesler
#
"""
Exercise 1.5.26 Amortized costs of the Erdös-Renyi model.
"""
# =============================================================================

import matplotlib.pyplot as plt

from ufcounter import cost_plot
from algs.unionfind import ErdosRenyi, WeightedQuickUnionUF

N = 625
g = ErdosRenyi(N, costs=True)

fig, ax = plt.subplots(num=1, clear=True, tight_layout=True)
cost_plot(g, ax=ax, title='Erdös-Renyi Model (Weighted Quick-Union)', y_max=10)

plt.show()

# =============================================================================
# =============================================================================
