#!/usr/bin/env python3
# =============================================================================
#     File: frequency_count_data.py
#  Created: 2019-11-16 18:03
#   Author: Bernie Roesler
# =============================================================================

"""Run FrequencyCounter to collect data on various symbol tables."""

from pathlib import Path

import numpy as np
import pandas as pd
from frequency_counter import FrequencyCounter

from algs.search import (
    BST,
    ArrayBST,
    ArrayST,
    BinarySearchST,
    RedBlackBST,
    # LinearProbingHashST,
    SeparateChainingHashST,
)

FORCE_UPDATE = False

DATA_PATH = Path(__file__).parent.parent / 'data'
PKL_PATH = Path(__file__).parent / 'pkl'

filenames = [
    DATA_PATH / 'tiny_tale.txt',  # 292
    # DATA_PATH / 'tale.txt',  # 779K
    # DATA_PATH / 'leipzig1m.txt',  # 124M
]

# TODO enumerate actual combinations allowed and code them
# e.g. "resize" only applies to SeparateChainingHashST, "selforg" only applies
# to ArrayST, etc.
# In plotting, should be able to compare, say, SeparateChainingHashST with and
# without resizing.

# (SeparateChainingHashST, resize=False, LL=False)
# (SeparateChainingHashST, resize=True, LL=False)
# (SeparateChainingHashST, resize=False, LL=True)
# (SeparateChainingHashST, resize=True, LL=True)
# (ArrayST, ins, selforg=False)
# (ArrayST, app, selforg=False)
# (ArrayST, ins, selforg=True)
# (ArrayST, app, selforg=True)

# NOTE ins/app relies on a source code change, not a dynamic argument,
# so maybe we should add that into ArrayST.

# NOTE LL relies on a source code change to SeparateChainingHashST to use
# ArrayST vs SequentialSearchST for the buckets. Default is SequentialSearchST,
# since that is what the book uses, but we could add an option.

# Options:
#   * resize: resize the hash table when load factor exceeds M (M=4 for testing)
#   * ins/app: insert(0, k) vs. append(k) to end of list (for ArrayST)
#   * selforg: self-organizing list (for ArrayST)
#   * LL: use linked list (SequentialSearchST) instead of ArrayST for
#     SeparateChainingHashST

kind = 'app'  # 'ins', 'app', 'selforg', 'LL', 'resize'

selforg = kind == 'selforg'
resize = kind == 'resize'
M = 997 if not resize else 4

data = []

# for ST in [SequentialSearchST]:
for ST in [ArrayST, BinarySearchST, BST, ArrayBST, RedBlackBST]:
    # for ST in [SeparateChainingHashST, LinearProbingHashST]:
    print(f"Running {ST.__name__}...")
    for filename in filenames:
        filestem = filename.stem

        for minlen in [1, 8, 10]:
            if ST is ArrayST:
                fc = FrequencyCounter(ST, selforg=selforg)
            elif ST is SeparateChainingHashST:
                fc = FrequencyCounter(ST, M=M, resize=resize)
            else:
                fc = FrequencyCounter(ST)

            fc.count_frequencies(filename, minlen)
            fc.find_max_word()

            # Store summary data
            run_id = f"{filestem}_{ST.__name__}_m{minlen:02d}_{kind}"
            trace_file = PKL_PATH / f"{run_id}.npz"

            data.append(
                {
                    'run_id': run_id,
                    'trace_file': str(trace_file),
                    'alg': ST.__name__,
                    'kind': kind,
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
    columns=["alg"],
    values=["words", "distinct", "max_word", "max_freq"],
)

print(print_df)

# =============================================================================
# =============================================================================
