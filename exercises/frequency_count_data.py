#!/usr/bin/env python3
# =============================================================================
#     File: frequency_count_data.py
#  Created: 2019-11-16 18:03
#   Author: Bernie Roesler
# =============================================================================

"""Run FrequencyCounter to collect data on various symbol tables."""

import json
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from frequency_counter import FrequencyCounter

from algs.search import (
    BST,
    ArrayBST,
    ArrayST,
    BinarySearchST,
    LinearProbingHashST,
    RedBlackBST,
    SeparateChainingHashST,
    SequentialSearchST,
)

FORCE_UPDATE = True

DATA_PATH = Path(__file__).parent.parent / 'data'
PKL_PATH = Path(__file__).parent / 'pkl' / 'frequency_count'
PKL_PATH.mkdir(parents=True, exist_ok=True)

filenames = [
    DATA_PATH / 'tiny_tale.txt',  # 292
    DATA_PATH / 'tale.txt',  # 779K
    # DATA_PATH / 'leipzig1m.txt',  # 124M
]

# Options:
#   * resize: resize the hash table when load factor exceeds M (M=4 for testing)
#   * ins/app: insert(0, k) vs. append(k) to end of list (for ArrayST)
#   * selforg: self-organizing list (for ArrayST)
#   * LL: use linked list (SequentialSearchST) instead of ArrayST for
#     SeparateChainingHashST

# All parameter combinations
params = {
    SequentialSearchST: [],
    ArrayST: ['append', 'selforg'],
    BinarySearchST: [],
    BST: [],
    ArrayBST: [],
    RedBlackBST: [],
    LinearProbingHashST: [],
    SeparateChainingHashST: ['resize', 'LL'],
}

# String map for the "kind" run_id
kind_map = {
    ('append', True): 'append',
    ('append', False): 'insert',
    ('selforg', True): 'selforg',
    ('selforg', False): '',
    ('resize', True): 'resize',
    ('resize', False): '',
    ('LL', True): 'Seq',
    ('LL', False): 'Arr',
}

data = []

for ST, kwarg_names in params.items():
    print(f"Running {ST.__name__}...")

    for filename in filenames:
        filestem = filename.stem

        for minlen in [1, 8, 10]:
            # Build kwargs for each ST
            if len(kwarg_names) == 0:
                all_kwarg_sets = [{}]  # just one set of kwargs (empty)
            else:
                # Generate all combinations of True/False for the given kwarg names
                all_kwarg_sets = []

                for combination in product([False, True], repeat=len(kwarg_names)):
                    kwargs = dict(zip(kwarg_names, combination))

                    if ST is SeparateChainingHashST:
                        kwargs['M'] = 4 if kwargs.get('resize', False) else 997

                    all_kwarg_sets.append(kwargs)

            for kwargs in all_kwarg_sets:
                # Build the "kind" string based on the kwargs
                kind = '_'.join(
                    kind_map.get((k, v), '') for k, v in kwargs.items() if k != 'M'
                ).strip('_')  # remove extraneous underscores
                kind = f"_{kind}" if kind else ''
                run_id = f"{filestem}_{ST.__name__}_m{minlen:02d}{kind}"
                trace_file = PKL_PATH / f"{run_id}.npz"

                # Run the frequency counter
                fc = FrequencyCounter(ST, **kwargs)
                fc.count_frequencies(filename, minlen)
                fc.find_max_word()

                # Store summary data
                data.append(
                    {
                        'run_id': run_id,
                        'trace_file': str(trace_file),
                        'alg': ST.__name__,
                        'kind': kind.lstrip('_'),
                        'kwargs': json.dumps(kwargs),
                        'minlen': minlen,
                        'filestem': filestem,
                        'words': fc.N,
                        'distinct': fc.t.size(),
                        'max_word': fc.max_word,
                        'max_freq': fc.t[fc.max_word],
                        'M': getattr(fc.t, 'M', None),  # for SeparateChainingHashST
                    }
                )

                np.savez_compressed(
                    trace_file,
                    cost=np.asarray(fc.cost),
                    time=np.asarray(fc.time),
                    allow_pickle=False,
                )


# Update existing summary file
summary_file = PKL_PATH / "frequency_count_summary.parquet"

if FORCE_UPDATE or not summary_file.exists():
    df = pd.DataFrame(data)
else:
    existing_df = pd.read_parquet(summary_file)
    new_df = pd.DataFrame(data)
    df = (
        pd.concat([existing_df, new_df], ignore_index=True)
        .drop_duplicates(subset=['run_id'], keep='last')
        .reset_index(drop=True)
    )

print(f"Writing summary data to {summary_file}...")
df.to_parquet(summary_file)

# For display only
print_df = pd.DataFrame(data).pivot(  # noqa: PD010
    index=["filestem", "minlen"],
    columns=["alg", "kind"],
    values=["words", "distinct", "max_word", "max_freq"],
)

print(print_df)

# =============================================================================
# =============================================================================
