#!/usr/bin/env python3
# =============================================================================
#     File: frequency_count_data.py
#  Created: 2019-11-16 18:03
#   Author: Bernie Roesler
#
"""
  Description: Run FrequencyCounter to collect data on various symbol tables.
"""
# =============================================================================

import os
import pandas as pd
import pickle

from algs.search import (ArrayST, BinarySearchST, BST, ArrayBST, RedBlackBST,
                         SeparateChainingHashST, LinearProbingHashST)
from frequency_counter import FrequencyCounter

filenames = ['../data/tiny_tale.txt',  # 292
             '../data/tale.txt']       # 779K
             # '../data/leipzig1m.txt']  # 124M

tags = [os.path.splitext(os.path.basename(x))[0] for x in filenames]
cols = pd.MultiIndex.from_product([tags, ['words', 'distinct', 'max_word', 'max_freq']])
kind = 'app'  # 'ins', 'app', 'selforg', 'LL', 'resize'
             #  for `.insert(0, item)` vs. `.append(item)`

selforg = True if kind == 'selforg' else False
resize = True if kind == 'resize' else False
M = 997 if not resize else 4

# for ST in [ArrayST, BinarySearchST, BST, ArrayBST, RedBlackBST]:
for ST in [SeparateChainingHashST, LinearProbingHashST]:
    df = pd.DataFrame(columns=cols)
    for i, f in enumerate(filenames):
        tag = tags[i]
        for minlen in [1, 8, 10]:
            if ST is ArrayST:
                fc = FrequencyCounter(ST, selforg=selforg)
            elif ST is SeparateChainingHashST:
                fc = FrequencyCounter(ST, M=M, resize=resize)
            else:
                fc = FrequencyCounter(ST)
            fc.count_frequencies(f, minlen)
            fc.find_max_word()
            df.loc[minlen, (tag, 'words')] = fc.N
            df.loc[minlen, (tag, 'distinct')] = fc.t.size
            df.loc[minlen, (tag, 'max_word')] = fc.max_word
            df.loc[minlen, (tag, 'max_freq')] = fc.t[fc.max_word]
            with open(f"./pkl/{tag}_{ST.__name__}_m{minlen:02d}_{kind}.pkl", 'wb') as fp:
                pickle.dump(fc, fp)

    print(df)

# =============================================================================
# =============================================================================
