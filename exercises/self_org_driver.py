#!/usr/bin/env python3
# =============================================================================
#     File: self_org_driver.py
#  Created: 2019-11-17 11:28
#   Author: Bernie Roesler
#
"""
    Description: Ex 3.1.33 Driver for self-organizing search.

    Write a driver program for self-organizing search implementations (see
    Exercise 3.1.22) that uses `get()` to fill a symbol table with N keys, then
    does 10 N successful searches according to a predefined probability
    distribution. Use this driver to compare the running time of your
    implementation from Exercise 3.1.22 with BinarySearchST for N = 1e3, 1e4,
    1e5, and 1e6 using the probability distribution where search hits the ith
    smallest key with probability 1/2^i.
"""
# =============================================================================

import gzip
import pickle
import time

import numpy as np

from pathlib import Path
from tqdm import tqdm

from algs.search import ArrayST, BinarySearchST

rng = np.random.default_rng(seed=565656)


class SelfOrganizingDriver():
    """Class to test self-organizing ArrayST.

    Parameters
    ----------
    ST : symbol table class
        The class of symbol table that will be used to store the frequencies.
    randinit : bool
        If True, insert the keys in random order, instead of increasing order.
    selforg : bool
        If True, use self-organizing search in the symbol table to cahce the
        results. Otherwise, leave the table unordered. Does not affect
        `BinarySearchST`, or other ordered symbol table classes.
    zipf : bool
        If True, choose the key for which to search with probability
        defined by the Zipf distribution::

            P(i) = 1 / (i * H_N(N))

        where `H_N` is the `N`th harmonic number. Otherwise, use the
        distribution::

            P(i) = `1/2^i`

    **kwargs : dict-like
        Any additional parameters will be passed to `ST`.

    Attributes
    ----------
    t : symbol table
        The symbol table where keys are words, and values are frequency counts.
    put_time : float
        The time it takes to `put` N items into the symbol table using the
        `run_test` method.
    get_time : float
        The time it takes to `get` 10*N items from the symbol table using the
        `run_test` method.
    runtimes : ndarray of floats
        The runtime of each `get` call performed during `run_test`. May be
        downsampled using the `samples` argument.
    """
    def __init__(self, ST, randinit=False, selforg=False, zipf=False):
        self.t = ST
        self._randinit = randinit
        self._selforg = selforg  # turn on caching in the symbol table.
        self._zipf = zipf    # choose probability distribution
        self.put_time = np.nan
        self.get_time = np.nan
        self.runtimes = np.empty((1,))

    @staticmethod
    @np.vectorize
    def H_N(N):
        r"""Harmonic number `N`.

        Parameters
        ----------
        N : array-like
            `N`th harmonic(s) desired.

        .. math::
            H_N = \sum\limits_{i=1}^N 1/i, \forall N = 1, 2, \dots, \infty

        Returns
        -------
        result : np.ndarray(float)
            `N`th harmonic numbers.
        """
        if N < 1:
            raise ValueError('H_N not defined for `N` < 1!')
        return np.sum(1.0 / np.arange(1, N+1))

    def run_test(self, N, samples=None, verbose=False):
        """Run the actual test by inserting `N` keys into the table, then
        performing `10N` successful searches.

        Parameters
        ----------
        N : int
            Number of keys to insert into the table.
        samples : int, optional, default=None
            Only store a random sample of the runtimes to save memory. The
            default stores all 10*N samples.
        verbose : bool
            Print extra messages and progress bars if True.

        Returns
        -------
        runtimes : ndarray, shape (samples, 1)
            The runtime of each `get` call performed. May be downsampled using
            the `samples` argument.
        """
        if verbose:
            print(f"Filling table with {N} keys...")

        keys = np.arange(1, N+1)  # skip 0 for probability functions

        # Pre-determined probability of searching for key `i`
        if self._zipf:
            probs = 1 / (keys * self.H_N(keys))
        else:
            probs = 1 / (2.0**keys)

        probs /= np.sum(probs)  # normalize to 1

        # Choose from keys in sorted order
        M = 10*N
        ks = rng.choice(keys, p=probs, size=M)

        if self._randinit:
            rng.shuffle(keys)     # insert in random order

        put_tic = time.perf_counter_ns()  # time the insertions separately

        # Fill the symbol table with keys (no values needed)
        self.t = self.t([(k, None) for k in keys], selforg=self._selforg)

        put_toc = time.perf_counter_ns()
        self.put_time = put_toc - put_tic

        if verbose:
            print('Performing 10N successful searches...')
        self.runtimes = np.empty(M)

        # Search for 10*N keys
        iterator = tqdm(ks, total=M) if verbose else ks
        get_tic = time.perf_counter_ns()

        for i, k in enumerate(iterator):
            tic = time.perf_counter_ns()
            self.t[k]  # perform get operation
            toc = time.perf_counter_ns()
            self.runtimes[i] = toc - tic

        get_toc = time.perf_counter_ns()
        self.get_time = get_toc - get_tic

        # only store subset of runtimes values
        if samples and samples <= M:
            idx = rng.integers(0, M, size=samples)
            self.runtimes = self.runtimes[idx]

        return self.runtimes  # also include return value


if __name__ == '__main__':
    # Define sequence of N to test
    # NOTE anything over ~1e4 takes almost untenably long. 1e5 takes 1.5 hrs.
    # Ns = [int(x) for x in [1e3, 1e4, 1e5, 1e6]]  # book values
    Ns = [int(x) for x in [1e2, 3e2, 1e3, 3e3, 1e4, 3e4, 1e5]]
    N_s = 100  # number of search times to sample for statistics

    dists = ['p', 'zipf']
    STs = [ArrayST, ArrayST, BinarySearchST]
    ST_names = ['SST', 'SST_selforg', 'BinarySearchST']
    selforgs = [False, True, False]

    drivers = dict()

    for N in Ns:
        for d in dists:
            for ST, ST_name, selforg in zip(STs, ST_names, selforgs):
                print(f"{ST_name=}, {selforg=}, {d=}")
                zipf = True if d == 'zipf' else 'p'
                driver = SelfOrganizingDriver(ST, zipf=zipf, selforg=selforg)
                driver.run_test(N, samples=N_s, verbose=True)

                # Store data
                drivers[(d, ST_name, N)] = driver

        # Write data to file (overwrite each loop in case it breaks)
        filename = Path('./pkl/self_org_drivers.pkl.gz')
        print(f"Writing to {filename}...", end='')
        with gzip.open(filename, 'wb') as f:
            pickle.dump(drivers, f)
        print('done.')

# =============================================================================
# =============================================================================
