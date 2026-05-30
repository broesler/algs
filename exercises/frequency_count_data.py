#!/usr/bin/env python3
# =============================================================================
#     File: frequency_count_data.py
#  Created: 2019-11-16 18:03
#   Author: Bernie Roesler
# =============================================================================

"""Run FrequencyCounter to collect data on various symbol tables."""

import pickle
from pathlib import Path

import pandas as pd
from frequency_counter import FrequencyCounter

from algs.search import (
    ArrayST,
    LinearProbingHashST,
    SeparateChainingHashST,
)

DATA_PATH = Path(__file__).parent.parent / 'data'
PKL_PATH = Path(__file__).parent / 'pkl'

filenames = [
    DATA_PATH / 'tiny_tale.txt',  # 292
    # DATA_PATH / 'tale.txt',  # 779K
    # DATA_PATH / 'leipzig1m.txt',  # 124M
]

# TODO document each of these options
kind = 'resize'  # 'ins', 'app', 'selforg', 'LL', 'resize'
#  for `.insert(0, item)` vs. `.append(item)`

selforg = True if kind == 'selforg' else False
resize = True if kind == 'resize' else False
M = 997 if not resize else 4

# for ST in [ArrayST, BinarySearchST, BST, ArrayBST, RedBlackBST]:
for ST in [SeparateChainingHashST, LinearProbingHashST]:
    for f in filenames:
        data = []
        tag = f.stem
        for minlen in [1, 8, 10]:
            if ST is ArrayST:
                fc = FrequencyCounter(ST, selforg=selforg)
            elif ST is SeparateChainingHashST:
                fc = FrequencyCounter(ST, M=M, resize=resize)
            else:
                fc = FrequencyCounter(ST)

            fc.count_frequencies(f, minlen)
            fc.find_max_word()

            data.append(
                {
                    'minlen': minlen,
                    'tag': tag,
                    'words': fc.N,
                    'distinct': fc.t.size(),
                    'max_word': fc.max_word,
                    'max_freq': fc.t[fc.max_word],
                }
            )

            df = (
                pd.DataFrame(data)  # noqa
                .pivot(
                    index="minlen",
                    columns="tag",
                    values=["words", "distinct", "max_word", "max_freq"],
                )
                .swaplevel(axis=1)
                .sort_index(axis=1)
            )

            pkl_file = PKL_PATH / f"{tag}_{ST.__name__}_m{minlen:02d}_{kind}.pkl"
            with pkl_file.open('wb') as fp:
                pickle.dump(fc, fp)

    print(df)

# =============================================================================
# =============================================================================
