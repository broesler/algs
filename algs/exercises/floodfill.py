#!/usr/bin/env python3
# =============================================================================
#     File: floodfill.py
#  Created: 2022-06-20 22:57
#   Author: Bernie Roesler
#
"""
Exercise 4.1.38: Implement flood fill image processing on the implicit
connectivity defined by connecting adjacent points that have the same color in
an image.

See Also
--------
[MATLAB bwconncomp](https://www.mathworks.com/help/images/ref/bwconncomp.html)
"""
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np

from algs.graph import Graph, CC

# Define example array
BW = np.array([[1, 1, 1, 0, 0, 0, 0, 0],
               [1, 1, 1, 0, 1, 1, 0, 0],
               [1, 1, 1, 0, 1, 1, 0, 0],
               [1, 1, 1, 0, 0, 0, 1, 0],
               [1, 1, 1, 0, 0, 0, 1, 0],
               [1, 1, 1, 0, 0, 0, 1, 0],
               [1, 1, 1, 0, 0, 1, 1, 0],
               [1, 1, 1, 0, 0, 0, 0, 0]])

# Connected components expectation
CC = np.array([[1, 1, 1, 0, 0, 0, 0, 0],
               [1, 1, 1, 0, 2, 2, 0, 0],
               [1, 1, 1, 0, 2, 2, 0, 0],
               [1, 1, 1, 0, 0, 0, 3, 0],
               [1, 1, 1, 0, 0, 0, 3, 0],
               [1, 1, 1, 0, 0, 0, 3, 0],
               [1, 1, 1, 0, 0, 3, 3, 0],
               [1, 1, 1, 0, 0, 0, 0, 0]])

# Steps:
#   * convert image array into a graph -> each pixel is a vertex, edges
#     between pixels that are the same color
#   * find connected components of the graph
#   * perform flood fill operation to change all pixels in a component
#   * convert graph back to array.


fig = plt.figure(1, clear=True, constrained_layout=True)
ax = fig.add_subplot()
# ax.imshow(BW, cmap='gray')
ax.imshow(CC, cmap='gray')
# ax.axis('off')

plt.show()
# =============================================================================
# =============================================================================
