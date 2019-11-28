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

import pickle
import time

import numpy as np
import pandas as pd

from pathlib import Path
from tqdm import tqdm

from algs.search import SequentialSearchST, BinarySearchST

class SelfOrganizingDriver():
    """Class to test self-organizing SequentialSearchST.

    Parameters
    ----------
    ST : symbol table class
        The class of symbol table that will be used to store the frequencies.
    cache : bool
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
    """
    def __init__(self, ST, cache=False, zipf=False):
        self.t= ST
        self.cache = cache
        self.zipf = zipf
        self.put_time = np.nan
        self.get_time = np.nan
        self.runtimes = np.empty((1,))

    @staticmethod
    @np.vectorize
    def H_N(N):
        """Harmonic number `N`.

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
            raise ValueError(f'H_N not defined for `N` < 1!')
        return np.sum([(1.0 / i) for i in np.arange(1, N+1)]) 

    def run_test(self, N, samples=None, verbose=False):
        """Run the actual test by inserting `N` keys into the table, then
        performing `10N` successful searches.

        Parameters
        ----------
        N : int
            Number of keys to insert into the table.
        samples : int, optional, default=None
            Only store a random sample of the runtimes to save memory.
        verbose : bool
            Print extra messages and progress bars if True.
        """
        if verbose:
            print(f"Filling table with {N} keys...")

        keys = np.arange(1, N+1)  # skip 0 for probability functions

        # Pre-determined probability of searching for key `i`
        if self.zipf:
            probs = 1 / (keys * self.H_N(keys))
        else:
            probs = 1 / (2.0**keys)

        probs /= np.sum(probs)  # normalize to 1

        np.random.shuffle(keys)        # random insertion order
        put_tic = time.perf_counter()  # time the insertions separately

        # Fill the symbol table with keys (no values needed)
        self.t = self.t([(k, None) for k in keys], cache=self.cache)

        put_toc = time.perf_counter()
        self.put_time = put_toc - put_tic

        if verbose:
            print(f"Performing 10N successful searches...")
        M = 10*N
        self.runtimes = np.empty(M)

        iterator = tqdm(range(M), total=M) if verbose else range(M) 
        get_tic = time.perf_counter()
        for i in iterator:
            k = np.random.choice(keys, p=probs)

            tic = time.perf_counter()
            x = self.t[k]  # perform get operation
            toc = time.perf_counter()

            self.runtimes[i] = toc - tic

        get_toc = time.perf_counter()
        self.get_time = get_toc - get_tic

        # only store subset of runtimes values
        if samples and samples <= M:
            idx = np.random.randint(0, M, size=samples)
            self.runtimes = self.runtimes[idx]


if __name__ == '__main__':
    # Define sequence of N to test
    # Ns = [int(x) for x in [10, 1e2, 1e3, 2e3, 5e3, 1e4]]
    Ns = [int(x) for x in [10, 1e2, 1e3]]
    N_s = 100  # number of search times to sample

    dists = ['p', 'zipf']
    STs = [SequentialSearchST, SequentialSearchST, BinarySearchST]
    ST_names = ['SST', 'SST_cached', 'BinarySearchST']
    caches = [False, True, False]

    drivers = dict()

    for N in Ns:
        for d in dists:
            for ST, ST_name, cache in zip(STs, ST_names, caches):
                zipf = True if d == 'zipf' else 'p'
                driver = SelfOrganizingDriver(ST, zipf=zipf, cache=cache)
                driver.run_test(N, samples=N_s, verbose=True)

                # Store data
                drivers[(d, ST_name, N)] = driver

    # Write data to file
    filename = Path(f"./pkl/self_org_drivers.pkl")
    with open(filename, 'wb') as f:
        pickle.dump(drivers, f)

# =============================================================================
# =============================================================================
