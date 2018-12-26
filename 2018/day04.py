#!/Users/bernardroesler/anaconda3/bin/python3
#==============================================================================
#     File: day04.py
#  Created: 2018-12-20 20:42
#   Author: Bernie Roesler
#
"""
  Description:
"""
#==============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns

import re
from datetime import datetime

# Parse '[YYYY-mm-dd HH:MM] Message' string
pat1 = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] (.+)')

def parse_line(line):
    """Get info from a line of the log file."""
    match = pat1.match(line)
    if match:
        return match[1], match[2]

#------------------------------------------------------------------------------ 
#        Main
#------------------------------------------------------------------------------
filename = 'data/input04.dat'
df = pd.DataFrame(columns=['time', 'msg'])

with open(filename, 'r') as f:
    for line in f:
        time, msg = parse_line(line.rstrip())
        df = df.append({'time':time, 'msg':msg}, ignore_index=True)

# Convert time column to actual timestamp
# NOTE pd.to_datetime() fails because pandas can only represent (1677-2262),
# see: <http://pandas-docs.github.io/pandas-docs-travis/timeseries.html#timeseries-timestamp-limits>
# Steps: 
#   * Convert column to datetime
#   * Change year to 2012, i.e.
#   * Use pandas to_datetime()

df['time'] = df['time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'))

#==============================================================================
#==============================================================================
