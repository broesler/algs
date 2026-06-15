#!/usr/bin/env python3
# =============================================================================
#     File: dairyqueen_graph.py
#  Created: 2026-06-15 14:16
#   Author: Bernie Roesler
# =============================================================================

"""Exercise 4.1.44: Real-world graph."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from algs.graph.random import random_simple_graph
from algs.graph.undirected import EuclideanGraph, SymbolGraph

DATA_PATH = Path(__file__).resolve().parents[1] / 'data'

rng = np.random.default_rng(seed=20240701)

V, E = 500, 500

df = pd.read_csv(DATA_PATH / 'dairyqueen.csv', header=None)
df.columns = ['lat', 'lon', 'name', 'address']
tf = df.sample(n=V, random_state=rng)

# Build a symbol graph using the names of the restaurants
sg = SymbolGraph(keys=tf['name'])
G = random_simple_graph(V, E)
sg._G = EuclideanGraph(G, x=tf['lat'], y=tf['lon'])

# -----------------------------------------------------------------------------
#         Plot the graph
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(num=1, clear=True)

sg.graph.draw(ax=ax, vkws={'s': 10, 'alpha': 0.4}, ekws={'lw': 1, 'alpha': 0.2})

plt.show()


# =============================================================================
# =============================================================================
