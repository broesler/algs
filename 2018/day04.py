#!/usr/bin/env python3
#==============================================================================
#     File: day04.py
#  Created: 2018-12-20 20:42
#   Author: Bernie Roesler
#
"""
  Description:
"""
#==============================================================================

import re
import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns

from sklearn.neighbors.kde import KernelDensity

PLOT_FLAG = True
MIN_HR = 60
BIN_EDGES = np.arange(MIN_HR+1)

# Parse '[YYYY-mm-dd HH:MM] Message' string
pat1 = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] (.+)')
id_pat = re.compile(r'Guard #(\d+) .*')

# kernel density estimator
kde = KernelDensity(kernel='gaussian', bandwidth=5)
xp = np.linspace(-1, 60, 1000).reshape(-1, 1)

def parse_line(line):
    """Get info from a line of the log file."""
    match = pat1.match(line)
    if match:
        return match[1], match[2]

def init_histogram():
    """Return array of integers for each minute asleep."""
    return np.bincount([], minlength=MIN_HR)

def gen_histograms(df):
    """Generate dictionary of guards' histograms of minutes asleep."""
    # Initialize values
    guards = dict()  # key == guard id
    awake_time = datetime.datetime(1, 1, 1)
    asleep_time = datetime.datetime(1, 1, 1)

    # Keep: guards[guard_id] == {'total':int, 'hist':df(pd.Period('1 hr'), int)}
    #   hist == period of 1 hr, histogram of minutes asleep
    for i, row in df.iterrows():
        # Parse message
        match = id_pat.match(row['msg'])
        # New guard on shift
        if match:
            awake_time = row['time']
            guard_id = int(match[1])
            # Initialize guard entry
            if guard_id not in guards:
                guards[guard_id] = {'total': 0,
                                    'hist': init_histogram()}
            continue  # go to next event

        elif row['msg'] == 'falls asleep':
            asleep_time = row['time']

        elif row['msg'] == 'wakes up':
            awake_time = row['time']

        else:
            raise ValueError(f"Message \'{row['msg']}\' not recognized!")

        # Populate histogram for current guard
        update_guards(guards[guard_id], awake_time, asleep_time)

    return guards

def update_guards(guard, awake_time, asleep_time):
    """Update total hours slept and histogram of minutes asleep.
        
    :param guard: dict with 'total', 'hist' keys.
    :type guard: dict.
    :param awake_time: datetime guard awoke.
    :type awake_time: datetime.datetime.
    :param asleep_time: datetime guard fell asleep.
    :type asleep_time: datetime.datetime.
    :returns: None    
    """
    r = pd.period_range(asleep_time, awake_time, freq='min')
    if not r.empty:
        counts = np.bincount(r.minute.values, minlength=MIN_HR)
        guard['hist'] += counts
        guard['total'] = np.sum(guard['hist'])  # total minutes slept
    return

def find_laziest_guard(guards):
    """Return id of guard with most minutes asleep."""
    max_minutes = 0
    max_id = -1
    for guard_id in guards.keys():
        guard = guards[guard_id]
        if guard['total'] > max_minutes:
            max_minutes = guard['total']
            max_id = guard_id
    return max_id

def find_max_minute(guard):
    """Return minute where guard is asleep the most."""
    return guard['hist'].argmax()

def find_sleepiest_guard(guards):
    """Return id of guard with largest max value."""
    max_minutes = 0
    max_id = -1
    for guard_id in guards.keys():
        guard = guards[guard_id]
        g_max = find_max_minute(guard)
        if guard['hist'][g_max] > max_minutes:
            max_minutes = guard['hist'][g_max]
            max_id = guard_id
    return max_id

def plot_guard(guard_id, ax=None):
    """Plot guard's histogram of minutes asleep."""
    if not ax:
        ax = plt.gca()
    guard = guards[guard_id]

    # Plot kernel density estimate
    # data = invert_hist(BIN_EDGES, guard['hist']).reshape(-1, 1)
    # if data.size:
    #     kde.fit(data)
    #     fx = np.exp(kde.score_samples(xp))
    #     ax.plot(xp, fx, label=guard_id)

    # Plot histogram
    ax.bar(BIN_EDGES[:-1], guard['hist'],
           align='edge', width=1, alpha=0.2,
           label=guard_id)
    return

def invert_hist(bin_edges, hist):
    """Get data back from histogram."""
    return np.repeat(bin_edges[:-1], hist)

#------------------------------------------------------------------------------ 
#        Import data
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

df['time'] = df['time'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M'))

# Sort dataframe to chronological order
df = df.sort_values(by=['time']).reset_index(drop=True)

# Strategy 1: Find the guard that has the most minutes asleep. What minute does
# that guard spend asleep the most?
guards = gen_histograms(df)

max_guard = find_laziest_guard(guards)
max_minute = find_max_minute(guards[max_guard])

print('Solution 1: {:d}'.format(max_guard * max_minute))

max_guard = find_sleepiest_guard(guards)
max_minute = find_max_minute(guards[max_guard])

print('Solution 2: {:d}'.format(max_guard * max_minute))

if PLOT_FLAG:
    fig = plt.figure(1)
    fig.clf()
    ax = fig.add_subplot(111)
    ax.set_xlabel('minute')
    ax.set_ylabel('# asleep')
    for guard_id in guards.keys():
        plot_guard(guard_id, ax=ax)
    ax.legend()
    plt.show()

#==============================================================================
#==============================================================================
