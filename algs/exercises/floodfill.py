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

from algs.basics import Queue


def flood_fill(img, si, sj, c, conn=8):
    """Fill the adjacent pixels of the same color.

    Parameters
    ----------
    img : (M, N) array_like
        Grayscale image matrix of M vectors in N dimensions.
    i0, j0 : int
        Coordinate pixel from which to search.
    c : int
        The new color with which to fill the image.
    conn : int in [4, 8], optional
        Define the connectivity by the number of neighbors to consider.
        4 : Pixels are connected if their edges touch.
        8 : Pixels are connected if their edges or corners touch.

    Returns
    -------
    img : (M, N) ndarray
        A copy of the image with changed pixels.
    """
    img = np.asarray(img).copy()
    M, N = img.shape
    if not (0 <= si < M and 0 <= sj < N):
        raise ValueError(f"Index ({si=}, {sj=}) invalid for ({M}, {N}) image!")
    if conn not in [4, 8]:
        raise ValueError('`conn` must be one of [4, 8].')
    if img[si, sj] == c:
        return img
    else:
        prev_c = img[si, sj]

    def _is_valid(i, j):
        return (0 <= i < M and 0 <= j < N and img[i, j] == prev_c)

    def _adj(si, sj):
        """Return a list of adjacent indices to `(i, j)` in the image.

        Parameters
        ----------
        si, sj : int
            Index of the source pixel.

        Returns
        -------
        res : list of (2,) tuples
            Indices of adjacent pixels that are "connected" by having the same
            color as img[si, sj].
        """
        test = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
        if conn == 8:
            test += [(i-1, j-1), (i+1, j-1), (i-1, j+1), (i+1, j+1)]
        return [t for t in test if _is_valid(*t)]

    # Perform breadth-first search on the image
    q = Queue()
    img[si, sj] = c  # serves as "marked"
    q.enqueue((si, sj))
    while not q.is_empty:
        i, j = q.dequeue()
        for wi, wj in _adj(i, j):
            if img[wi, wj] != c:
                img[wi, wj] = c
                q.enqueue((wi, wj))
    return img


if __name__ == "__main__":
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

    # Fill the small square with a new color
    FF = flood_fill(BW, 1, 4, c=2)

    fig = plt.figure(1, clear=True, constrained_layout=True)
    gs = fig.add_gridspec(ncols=3)
    for i, (img, title) in enumerate(zip([BW, CC, FF], ['BW', 'CC', 'FF'])):
        ax = fig.add_subplot(gs[i])
        ax.imshow(img, cmap='plasma')
        ax.set_title(title)
        ax.axis('off')

    plt.show()

# =============================================================================
# =============================================================================
