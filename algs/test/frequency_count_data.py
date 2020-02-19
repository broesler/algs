#!/usr/bin/env python3
# =============================================================================
#     File: frequency_count.py
#  Created: 2019-11-16 18:03
#   Author: Bernie Roesler
#
"""
  Description:
"""
# =============================================================================

import os
import pandas as pd
import pickle

from algs.search import SequentialSearchST, BinarySearchST
from frequency_counter import FrequencyCounter

filenames = ['../data/tiny_tale.txt',  # 292
             '../data/tale.txt']       # 779K
             # '../data/leipzig1m.txt']  # 124M

tags = [os.path.splitext(os.path.basename(x))[0] for x in filenames]
cols = pd.MultiIndex.from_product([tags, ['words', 'distinct', 'max_word', 'max_freq']])

for ST in [SequentialSearchST, BinarySearchST]:
    df = pd.DataFrame(columns=cols)
    for i, f in enumerate(filenames):
        tag = tags[i]
        for minlen in [1, 8, 10]:
            fc = FrequencyCounter(ST)
            fc.count_frequencies(f, minlen)
            df.loc[minlen, (tag, 'words')] = fc.N
            df.loc[minlen, (tag, 'distinct')] = fc.t.size
            df.loc[minlen, (tag, 'max_word')] = fc.max_word
            df.loc[minlen, (tag, 'max_freq')] = fc.t[fc.max_word]
            pickle.dump(fc, open(f"./pkl/{tag}_{ST.__name__}_m{minlen:02d}.pkl", 'wb'))

    print(df)

# =============================================================================
# =============================================================================
